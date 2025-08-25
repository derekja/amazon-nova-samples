import boto3
import base64
import json
import logging
import os
import numpy as np
from scipy import signal

logger = logging.getLogger(__name__)

class PollyService:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.polly_client = boto3.client('polly', region_name=region)
    
    async def generate_speech(self, text, voice_id='matthew'):
        """Generate speech using AWS Polly and return base64 encoded audio."""
        try:
            # Convert voice_id to proper Polly format (title case)
            polly_voice_id = voice_id.title()
            logger.info(f"Starting Polly synthesis for text: '{text}' with voice: {voice_id} -> {polly_voice_id}")
            
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='pcm',
                VoiceId=polly_voice_id,
                SampleRate='16000'
            )
            
            # Get the audio stream
            audio_data = response['AudioStream'].read()
            logger.info(f"Polly returned {len(audio_data)} bytes of audio data")
            
            # Convert PCM bytes to numpy array (16-bit signed integers)
            audio_samples = np.frombuffer(audio_data, dtype=np.int16)
            logger.info(f"Converted to {len(audio_samples)} audio samples")
            
            # Resample from 16000 Hz to 24000 Hz to match Nova Sonic
            original_sample_rate = 16000
            target_sample_rate = 24000
            num_samples = int(len(audio_samples) * target_sample_rate / original_sample_rate)
            resampled_audio = signal.resample(audio_samples, num_samples)
            
            # Convert back to int16
            resampled_audio = resampled_audio.astype(np.int16)
            logger.info(f"Resampled to {len(resampled_audio)} samples at {target_sample_rate} Hz")
            
            # Convert to bytes and then base64
            resampled_bytes = resampled_audio.tobytes()
            audio_base64 = base64.b64encode(resampled_bytes).decode('utf-8')
            logger.info(f"Base64 encoded audio length: {len(audio_base64)} characters")
            
            logger.info(f"Successfully generated speech for text: '{text}' using voice: {voice_id}")
            
            return {
                'event': {
                    'pollyAudioOutput': {
                        'content': audio_base64,
                        'voice': voice_id,
                        'text': text
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating speech with Polly: {e}")
            return {
                'event': {
                    'pollyError': {
                        'message': str(e),
                        'text': text
                    }
                }
            }