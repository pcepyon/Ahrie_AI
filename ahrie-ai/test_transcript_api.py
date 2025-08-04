"""Test youtube-transcript-api directly."""

from youtube_transcript_api import YouTubeTranscriptApi

# Test video ID (from the search results)
video_id = "uW2L38gaWFE"

print(f"Testing transcript API with video ID: {video_id}")
print("=" * 50)

try:
    # Create API instance
    api = YouTubeTranscriptApi()
    
    # Method 1: Fetch transcript
    print("\n1. Testing fetch transcript...")
    transcript = api.fetch(video_id)
    print(f"✅ Success! Got {len(transcript)} transcript segments")
    if transcript:
        print(f"First segment: {transcript[0]}")
        # Combine all text
        full_text = ' '.join([entry.text for entry in transcript])
        print(f"Total length: {len(full_text)} characters")
        print(f"Preview: {full_text[:200]}...")
    
    # Method 2: List available transcripts
    print("\n\n2. Testing list transcripts...")
    transcript_list = api.list(video_id)
    
    print("\nAvailable transcripts:")
    for lang_code, transcript_info in transcript_list.items():
        print(f"  - Language code: {lang_code}")
        if isinstance(transcript_info, dict):
            for key, value in transcript_info.items():
                print(f"    {key}: {value}")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()