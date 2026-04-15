import os
import uuid
import asyncio
import json
import librosa
from pydub import AudioSegment
from datetime import datetime

from . import stt
from . import translator
from . import emotion
from . import tts
from . import audio_utils
from . import prosody_enhancement
from . import vocal_separator
from .config import UPLOADS_DIR, OUTPUTS_DIR, LANGUAGE_VOICE_MAPS, TTS_RETRY_COUNT, USE_PROSODY_ENHANCEMENT, TRANSLATION_METHOD

class PipelineManager:
    def __init__(self):
        self.temp_dir = os.path.join(OUTPUTS_DIR, "temp")
        os.makedirs(self.temp_dir, exist_ok=True)

    async def process_audio_file(self, input_path, target_lang="ta"):
        """
        Executes the full professional dubbing pipeline with error recovery.
        Returns: (final_output_path, processed_segments, metadata)
        """
        job_id = str(uuid.uuid4())
        job_start_time = datetime.now()
        print(f"Starting Job: {job_id}")
        
        failed_segments = []
        
        try:
            # 1. Full Audio Transcription (Global Context First)
            print("[1/5] Transcribing full audio...")
            transcription_result = stt.transcribe_full_audio(input_path)
            full_text = transcription_result["text"]
            segments = transcription_result["segments"]
            print(f"Found {len(segments)} segments")
            
            # 2. Context-Aware Full Translation
            print("[2/5] Translating full text...")
            translated_segments = translator.translate_segments_in_context(segments, target_lang)
            
            # 3. Intelligent Segmentation & Emotion Mapping
            print("[3/5] Mapping emotions and characters...")
            full_audio_data = audio_utils.load_audio(input_path)
            
            # 4. Neural TTS Generation (Character-based) - with parallel processing
            print("[4/5] Generating speech synthesis...")
            voice_profiles = []
            segment_tasks = []
            
            for i, seg in enumerate(translated_segments):
                # Extract segment audio for emotion detection
                seg_audio_arr = audio_utils.split_segment(
                    full_audio_data,
                    seg["start"] * 1000,
                    seg["end"] * 1000
                )
                
                # Detect character features and emotion
                try:
                    features = emotion.detect_segment_emotion(seg_audio_arr)
                    voice_profile = emotion.get_character_voice_profile(features, lang=target_lang)
                except Exception as e:
                    print(f"Emotion detection failed for segment {i}: {e}, using default")
                    voice_profile = "male_adult_neutral"
                    features = {
                        "gender": "male",
                        "age": "adult",
                        "emotion": "neutral",
                        "pitch": 150,
                        "energy": 0.02
                    }
                
                voice_profiles.append(voice_profile)
                
                # Prepare segment for TTS
                seg_output_path = os.path.join(self.temp_dir, f"{job_id}_seg_{i}.mp3")
                optimized_text = translator.optimize_for_speech(seg["translated_text"])
                
                # Create async task for TTS
                task = self._generate_segment_with_retry(
                    i, optimized_text, voice_profile,
                    seg_output_path, target_lang, features, seg, input_path
                )
                segment_tasks.append(task)
            
            # Execute all TTS tasks in parallel
            print(f"Generating {len(segment_tasks)} speech segments in parallel...")
            tts_results = await asyncio.gather(*segment_tasks, return_exceptions=True)
            
            # Collect results and handle failures
            segment_audios = []
            metadata_segments = []
            
            for i, result in enumerate(tts_results):
                if isinstance(result, Exception):
                    print(f"Segment {i} generation failed: {result}")
                    failed_segments.append(i)
                else:
                    seg_output_path, seg_metadata = result
                    segment_audios.append(seg_output_path)
                    metadata_segments.append(seg_metadata)
            
            if not segment_audios:
                raise RuntimeError("All segments failed TTS generation")
            
            # 5. Audio Merge
            print("[5/5] Merging final audio...")
            final_output_path = os.path.join(OUTPUTS_DIR, f"{job_id}_final.mp3")
            self.merge_audio_segments(segment_audios, final_output_path)
            
            # Cleanup temp files
            for p in segment_audios:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except:
                        pass
            
            # Prepare metadata
            job_duration = (datetime.now() - job_start_time).total_seconds()
            metadata = {
                "job_id": job_id,
                "status": "success",
                "input_file": os.path.basename(input_path),
                "output_file": os.path.basename(final_output_path),
                "target_language": target_lang,
                "total_segments": len(translated_segments),
                "successful_segments": len(metadata_segments),
                "failed_segments": len(failed_segments),
                "processing_time_seconds": job_duration,
                "original_language": transcription_result.get("language", "unknown")
            }
            
            if failed_segments:
                metadata["failed_segment_indices"] = failed_segments
            
            # Save metadata file
            metadata_path = os.path.join(OUTPUTS_DIR, f"{job_id}_metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Job {job_id} completed in {job_duration:.1f}s")
            return final_output_path, metadata_segments, metadata
            
        except Exception as e:
            print(f"Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            raise

    async def _generate_segment_with_retry(
        self, idx, text, voice_profile, output_path, lang, features, segment, original_audio_path
    ):
        """
        Generates speech for a segment with retry logic.
        No stretching - let TTS generate naturally.
        Returns: (output_path, metadata)
        """
        import soundfile as sf
        
        original_duration = segment["end"] - segment["start"]
        
        for attempt in range(TTS_RETRY_COUNT):
            try:
                # Generate TTS audio - let it speak naturally
                await tts.generate_speech_async(text, voice_profile, output_path, lang=lang)
                
                # Create metadata for this segment
                seg_metadata = {
                    "start": segment["start"],
                    "end": segment["end"],
                    "duration": original_duration,
                    "emotion": features["emotion"],
                    "gender": features["gender"],
                    "age_group": features["age"],
                    "voice_profile": voice_profile,
                    "original_text": segment.get("text", ""),
                    "translated_text": segment.get("translated_text", ""),
                    "quality_enhanced": False
                }
                
                print(f"Segment {idx} generated successfully")
                return output_path, seg_metadata
                
            except Exception as e:
                if attempt < TTS_RETRY_COUNT - 1:
                    print(f"Segment {idx} generation failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(2 ** attempt)
                else:
                    print(f"Segment {idx} failed after {TTS_RETRY_COUNT} attempts: {e}")
                    raise

    def merge_audio_segments(self, segment_paths, output_path):
        """
        Merges generated segments into a single file.
        """
        if not segment_paths:
            raise ValueError("No segments to merge")
        
        try:
            combined = AudioSegment.empty()
            for p in segment_paths:
                if os.path.exists(p):
                    seg = AudioSegment.from_file(p)
                    combined += seg
            
            if combined.duration_seconds == 0:
                raise ValueError("Combined audio has zero duration")
            
            combined.export(output_path, format="mp3")
            print(f"Merged audio saved to {output_path}")
            return output_path
        except Exception as e:
            raise RuntimeError(f"Audio merge failed: {str(e)}")

    async def process_song(self, input_path, target_lang="ta"):
        """
        Processes songs by separating vocals, translating them, and remixing.
        
        Returns: (final_output_path, processed_segments, metadata)
        """
        job_id = str(uuid.uuid4())
        job_start_time = datetime.now()
        print(f"Starting Song Job: {job_id}")
        
        try:
            # Step 1: Vocal Separation
            print("[1/6] Separating vocals from instrumental...")
            vocals_path, instrumental_path = vocal_separator.separate_vocals_demucs(input_path)
            
            # Step 2: Transcribe vocals
            print("[2/6] Transcribing vocals...")
            transcription_result = stt.transcribe_full_audio(vocals_path)
            segments = transcription_result["segments"]
            print(f"Found {len(segments)} segments in vocals")
            
            # Step 3: Translate
            print("[3/6] Translating vocals...")
            translated_segments = translator.translate_segments_in_context(segments, target_lang)
            
            # Step 4: Generate TTS for vocals
            print("[4/6] Generating translated vocals...")
            translated_vocals_path = os.path.join(OUTPUTS_DIR, f"{job_id}_translated_vocals.mp3")
            full_audio_data = audio_utils.load_audio(vocals_path)
            
            segment_audios = []
            metadata_segments = []
            
            for i, seg in enumerate(translated_segments):
                # Skip instrumental segments - keep original audio
                if seg["translated_text"].lower().startswith("[") and seg["translated_text"].lower().endswith("]"):
                    print(f"Segment {i}: Keeping original instrumental audio ({seg['translated_text']})")
                    
                    # Add original audio segment directly (no TTS needed)
                    original_segment_path = os.path.join(self.temp_dir, f"{job_id}_seg_{i}_original.wav")
                    seg_audio_arr = audio_utils.split_segment(
                        full_audio_data,
                        seg["start"] * 1000,
                        seg["end"] * 1000
                    )
                    import soundfile as sf
                    sf.write(original_segment_path, seg_audio_arr, 16000)
                    
                    segment_audios.append(original_segment_path)
                    metadata_segments.append({
                        "start": seg["start"],
                        "end": seg["end"],
                        "duration": seg["end"] - seg["start"],
                        "emotion": "instrumental",
                        "gender": "n/a",
                        "age_group": "n/a",
                        "voice_profile": "instrumental",
                        "original_text": seg.get("text", ""),
                        "translated_text": seg.get("translated_text", "")
                    })
                    continue
                
                # Extract original vocal segment for characteristics
                seg_audio_arr = audio_utils.split_segment(
                    full_audio_data,
                    seg["start"] * 1000,
                    seg["end"] * 1000
                )
                
                # Detect emotion/characteristics
                try:
                    features = emotion.detect_segment_emotion(seg_audio_arr)
                    voice_profile = emotion.get_character_voice_profile(features, lang=target_lang)
                except Exception as e:
                    print(f"Emotion detection failed for segment {i}: {e}")
                    features = {"gender": "male", "age": "adult", "emotion": "neutral", "pitch": 150, "energy": 0.02}
                    voice_profile = "male_adult_neutral"
                
                # Generate TTS for this segment
                seg_output_path = os.path.join(self.temp_dir, f"{job_id}_seg_{i}.mp3")
                optimized_text = translator.optimize_for_speech(seg["translated_text"])
                original_duration = seg["end"] - seg["start"]
                
                try:
                    # Generate TTS - let it speak naturally without stretching
                    # Stretching causes audio artifacts and distortion
                    await tts.generate_speech_async(optimized_text, voice_profile, seg_output_path, lang=target_lang)
                    
                    print(f"Segment {i}: Generated TTS (duration: ~{original_duration:.2f}s target)")
                    
                    segment_audios.append(seg_output_path)
                    metadata_segments.append({
                        "start": seg["start"],
                        "end": seg["end"],
                        "duration": original_duration,
                        "emotion": features["emotion"],
                        "gender": features["gender"],
                        "age_group": features["age"],
                        "voice_profile": voice_profile,
                        "original_text": seg.get("text", ""),
                        "translated_text": seg.get("translated_text", "")
                    })
                    
                except Exception as e:
                    print(f"Segment {i} generation failed: {e}")
                    raise
            
            # Step 5: Merge all translated vocals
            print("[5/6] Merging translated vocal segments...")
            if segment_audios:
                self.merge_audio_segments(segment_audios, translated_vocals_path)
                
                # Cleanup temp files
                for p in segment_audios:
                    if os.path.exists(p):
                        try:
                            os.remove(p)
                        except:
                            pass
            else:
                raise RuntimeError("No vocal segments generated")
            
            # Step 6: Remix with original instrumental
            print("[6/6] Remixing with original instrumental...")
            final_output_path = os.path.join(OUTPUTS_DIR, f"{job_id}_final.mp3")
            vocal_separator.remix_audio(
                translated_vocals_path,
                instrumental_path,
                final_output_path,
                vocal_level=0.75,
                music_level=0.45
            )
            
            # Cleanup separation files
            for path in [vocals_path, instrumental_path, translated_vocals_path]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass
            
            # Create metadata
            job_duration = (datetime.now() - job_start_time).total_seconds()
            metadata = {
                "job_id": job_id,
                "status": "success",
                "input_file": os.path.basename(input_path),
                "output_file": os.path.basename(final_output_path),
                "audio_type": "song",
                "target_language": target_lang,
                "total_segments": len(translated_segments),
                "successful_segments": len(metadata_segments),
                "processing_time_seconds": job_duration,
                "pipeline": "vocal_separation + translation + remix"
            }
            
            print(f"Song Job {job_id} completed in {job_duration:.1f}s")
            return final_output_path, metadata_segments, metadata
            
        except Exception as e:
            print(f"Song processing failed: {e}")
            import traceback
            traceback.print_exc()
            raise

pipeline_manager = PipelineManager()
