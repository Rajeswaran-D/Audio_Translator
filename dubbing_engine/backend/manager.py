import os
import uuid
import asyncio
from pydub import AudioSegment

from . import stt
from . import translator
from . import emotion
from . import tts
from . import audio_utils
from .config import UPLOADS_DIR, OUTPUTS_DIR

class PipelineManager:
    def __init__(self):
        self.temp_dir = os.path.join(OUTPUTS_DIR, "temp")
        os.makedirs(self.temp_dir, exist_ok=True)

    async def process_audio_file(self, input_path, target_lang="ta"):
        """
        Executes the full professional dubbing pipeline.
        """
        job_id = str(uuid.uuid4())
        print(f"Starting Job: {job_id}")
        
        # 1. Full Audio Transcription (Global Context First)
        print("Transcribing full audio...")
        transcription_result = stt.transcribe_full_audio(input_path)
        full_text = transcription_result["text"]
        segments = transcription_result["segments"]
        
        # 2. Context-Aware Full Translation
        print("Translating full text...")
        translated_segments = translator.translate_segments_in_context(segments, target_lang)
        
        # 3. Intelligent Segmentation & Emotion Mapping
        print("Mapping emotions and characters...")
        full_audio_data = audio_utils.load_audio(input_path)
        
        segment_audios = []
        for i, seg in enumerate(translated_segments):
            # Extract segment audio for emotion detection
            seg_audio_arr = audio_utils.split_segment(full_audio_data, seg["start"]*1000, seg["end"]*1000)
            
            # Detect character features and emotion
            features = emotion.detect_segment_emotion(seg_audio_arr)
            voice_profile = emotion.get_character_voice_profile(features)
            
            # 4. Neural TTS Generation (Character-based)
            seg_output_path = os.path.join(self.temp_dir, f"{job_id}_seg_{i}.mp3")
            optimized_text = translator.optimize_for_speech(seg["translated_text"])
            
            print(f"Generating segment {i} ({voice_profile})...")
            await tts.generate_speech_async(optimized_text, voice_profile, seg_output_path, lang=target_lang)
            
            # Save metadata for frontend
            seg_metadata = {
                "start": seg["start"],
                "end": seg["end"],
                "emotion": features["emotion"],
                "gender": features["gender"],
                "age_group": features["age"],
                "translated_text": seg["translated_text"]
            }
            seg["metadata"] = seg_metadata
            segment_audios.append(seg_output_path)
            
        # 5. Audio Merge
        print("Merging final audio...")
        final_output_path = os.path.join(OUTPUTS_DIR, f"{job_id}_final.mp3")
        self.merge_audio_segments(segment_audios, final_output_path)
        
        # Cleanup temp files
        for p in segment_audios:
            if os.path.exists(p): os.remove(p)
            
        return final_output_path, [s["metadata"] for s in translated_segments]

    def merge_audio_segments(self, segment_paths, output_path):
        """
        Merges generated segments into a single file.
        """
        combined = AudioSegment.empty()
        for p in segment_paths:
            seg = AudioSegment.from_file(p)
            combined += seg
        combined.export(output_path, format="mp3")
        return output_path

pipeline_manager = PipelineManager()
