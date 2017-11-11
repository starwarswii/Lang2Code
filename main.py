import speech_recognition as sr

r = sr.Recognizer()
m = sr.Microphone()

try:
    print("be silent")
    with m as source:
        r.adjust_for_ambient_noise(source)
    print("minimum energy threshold: {}".format(r.energy_threshold))
    
    while True:
        try:
        
            print("listening")
            with m as source:
                audio = r.listen(source)
            print("recognizing")
            
            value = r.recognize_google(audio)

            print(value)
             
        except sr.UnknownValueError:
            print("didn't hear you")
        except sr.RequestError as e:
            print("request error: {}".format(e))
            
except KeyboardInterrupt:
    pass
