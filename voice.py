from gtts import gTTS
import pygame
import io
# pip install gtts pygame

class VOIC:
    def __init__(self,choice=''):
        self.languages = {
            '1': ('en', 'English'),
            '2': ('es', 'Spanish'),
            '3': ('fr', 'French'),
            '4': ('de', 'German'),
            '5': ('zh', 'Chinese')
        }
        self.selected_language = None
        self.select_language(choice)
        pygame.mixer.init()
    def show_language(self):
        print("Available languages:")
        for index, (lang_code, lang_name) in self.languages.items():
            print(f"{index}. {lang_name}")
        
    def select_language(self,choice):
        
        while True:
            if choice in self.languages:
                self.selected_language = self.languages[choice][0]
                print(f"Selected language: {self.languages[choice][1]}")
                break
            else:
                print("Invalid choice. Please select a valid number.")
                choice = input('failed please choose: ')

    def speak(self, text=""):
        if text == "":
            return
        tts = gTTS(text=text, lang=self.selected_language)
        with io.BytesIO() as audio_file:
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            pygame.mixer.music.load(audio_file, 'mp3')
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

# Example usage:
if __name__ == "__main__":
    tts = VOIC('1')
    tts.speak("Welcome Back")
