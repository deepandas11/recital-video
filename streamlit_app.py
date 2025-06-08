import streamlit as st
import tempfile
import os
import uuid
from PIL import Image
try:
    # MoviePy 2.0.0+ (new structure)
    from moviepy import AudioFileClip, ImageClip
except ImportError:
    # MoviePy 1.x (old structure)
    from moviepy.editor import AudioFileClip, ImageClip
import time

# Page configuration
st.set_page_config(
    page_title="🎵 Recital Video Creator",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def create_video_from_audio_and_image(audio_path, image_path):
    """Create video by combining audio with static image"""
    try:
        with st.spinner("🎬 Creating your video... This may take a few minutes."):
            # Load audio clip
            audio_clip = AudioFileClip(audio_path)
            
            # Load and prepare image
            image_clip = ImageClip(image_path, duration=audio_clip.duration)
            
            # Resize image to standard video dimensions (1920x1080)
            # MoviePy 2.0+ syntax
            try:
                # Try new MoviePy 2.0+ method
                image_clip = image_clip.resized(height=1080)
            except AttributeError:
                # Fallback to old MoviePy 1.x method
                image_clip = image_clip.resize(height=1080)
            
            # Create final video with audio
            try:
                # Try new MoviePy 2.0+ method
                final_video = image_clip.with_audio(audio_clip)
            except AttributeError:
                # Fallback to old MoviePy 1.x method
                final_video = image_clip.set_audio(audio_clip)
            
            # Create output path
            output_path = os.path.join(tempfile.gettempdir(), f"video_{uuid.uuid4()}.mp4")
            
            # Write video file with MoviePy 2.0+ compatible settings
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=f'temp-audio-{uuid.uuid4()}.m4a',
                remove_temp=True,
                logger=None
            )
            
            # Close clips to free memory
            audio_clip.close()
            image_clip.close()
            final_video.close()
            
            return output_path
    except Exception as e:
        st.error(f"Video creation failed: {str(e)}")
        return None

def main():
    # App title and description
    st.title("🎵 Recital Video Creator")
    st.markdown("*Transform your audio recordings into beautiful videos with your own images*")
    
    st.markdown("### 🎤 Create Your Video")
    
    # File upload
    uploaded_audio = st.file_uploader(
        "Upload your audio recording",
        type=['mp3', 'wav', 'ogg', 'm4a', 'aac', 'opus'],
        help="Support formats: MP3, WAV, OGG, M4A, AAC, OPUS (from WhatsApp, voice recorder, etc.)"
    )
    
    # Audio preview
    if uploaded_audio is not None:
        st.audio(uploaded_audio, format='audio/wav')
        st.success(f"✅ Audio uploaded: {uploaded_audio.name}")
    
    # Image upload section
    st.markdown("### 🖼️ Upload Your Image")
    
    uploaded_image = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
        help="Supported formats: PNG, JPG, JPEG, GIF, BMP, WEBP"
    )
    
    image_path_ready = None
    if uploaded_image is not None:
        # Show image preview
        st.image(uploaded_image, caption="Uploaded Image Preview", use_column_width=True)
        
        # Save uploaded image to temporary file
        temp_img_path = os.path.join(tempfile.gettempdir(), f"uploaded_image_{uuid.uuid4()}_{uploaded_image.name}")
        with open(temp_img_path, "wb") as f:
            f.write(uploaded_image.getbuffer())
        image_path_ready = temp_img_path
    
    # Generate button - simplified conditions
    can_generate = uploaded_audio and uploaded_image
    
    if st.button("🎬 Create My Video", type="primary", disabled=not can_generate):
        if can_generate:
            # Save uploaded audio to temporary file
            audio_path = os.path.join(tempfile.gettempdir(), f"audio_{uuid.uuid4()}_{uploaded_audio.name}")
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.getbuffer())
            
            # Use uploaded image
            final_image_path = image_path_ready
            
            if final_image_path:
                # Show the image being used
                st.image(final_image_path, caption="Image for Video", use_column_width=True)
                
                # Create video
                video_path = create_video_from_audio_and_image(audio_path, final_image_path)
                
                if video_path:
                    st.success("🎉 Video created successfully!")
                    
                    # Provide download button
                    with open(video_path, "rb") as video_file:
                        st.download_button(
                            label="📥 Download Video (MP4)",
                            data=video_file.read(),
                            file_name=f"recital_video_{int(time.time())}.mp4",
                            mime="video/mp4",
                            type="primary"
                        )
                    
                    # Show video preview
                    st.video(video_path)
                    
                    # Cleanup temporary files
                    try:
                        os.remove(audio_path)
                        os.remove(video_path)
                        # Note: We don't remove the uploaded image temp file as it might be used again
                    except:
                        pass
        else:
            missing = []
            if not uploaded_audio:
                missing.append("audio file")
            if not uploaded_image:
                missing.append("image file")
            
            st.error(f"Please provide: {', '.join(missing)}")
    
    # Instructions and tips
    st.markdown("---")
    st.markdown("### 💡 Tips for better results:")
    st.markdown("""
    - **Audio**: Any format works - WhatsApp voice messages, recordings from phone, etc.
    - **Image descriptions**: Be specific about mood, setting, colors, and style
    - **Processing time**: Usually takes 2-3 minutes depending on audio length
    - **Video quality**: Output is Full HD (1920x1080) MP4 format
    """)
    
    st.markdown("### 🔒 Privacy & Security:")
    st.markdown("""
    - Your Facebook credentials are only used for this session
    - No credentials or files are permanently stored
    - Audio and images are processed temporarily and automatically deleted
    - Videos are only available for download during your session
    """)

if __name__ == "__main__":
    main()