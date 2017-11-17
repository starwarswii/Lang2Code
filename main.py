import speech_recognition as sr
import re
import csv

def replacement_language_to_regex(pattern_replacement_pair):
    (pattern, replacement) = pattern_replacement_pair

    pattern = re.sub("W", r"(\w+)", pattern)
    #find a number that doesn't follow a letter (not thing1) and optionally has a plus or minus sign and a decimal place
    pattern = re.sub("D", r"((?<![a-zA-Z])[-+]?\d*\.?\d+)", pattern)
    #just an or(|) of W and D
    pattern = re.sub("B", r"((?<![a-zA-Z])[-+]?\d*\.?\d+|\w+)", pattern)
    #W plus spaces (used for strings)
    pattern = re.sub("S", r"(\w[\w\s]*)", pattern)
    pattern = "^"+pattern+"$"

    #we have to pass a function for the replace option because otherwise everything becomes \1
    replacement = re.sub(r"\d+", lambda x: "\\"+x.group(0), replacement)
    
    return (pattern, replacement)

#Takes all the data and puts it into a list of tuples of (Regex, Python Code, 1 or 0)
def read_replacements_plus_indent():
    replacements_plus_indent = []

    #returns only the non commented and non-empty lines
    def skip_comments_and_blanks(file):
        for line in file:
            line = line.strip()
            if line and not line[0] == "#":
                yield line

    csv.register_dialect("replacements", delimiter=",", doublequote=True, escapechar=None, lineterminator="\r\n", quotechar="\"", quoting=csv.QUOTE_NONNUMERIC, skipinitialspace=True)

    #newline="" is a recommended argument by the csv parser spec
    file = open("replacements.csv", "r", newline="")
    csvfile = csv.reader(skip_comments_and_blanks(file), dialect="replacements")
    
    for row in csvfile:
        row_tuple = tuple(row)
        #print(row_tuple)
        if (len(row_tuple) == 2):
            #star indicates unknown number of elements. adds a 0 to the end, making it a triple
            replacements_plus_indent.append((*replacement_language_to_regex(row_tuple), 0))
        else:
            replacements_plus_indent.append((*replacement_language_to_regex(row_tuple[:2]), int(row_tuple[2])))
            
    return replacements_plus_indent

def convert_to_code_plus_indent(raw_text, replacements_plus_indent):
    for (pattern, replace, indent_level) in replacements_plus_indent:
        if (re.match(pattern, raw_text)):
            return (re.sub(pattern, replace, raw_text), indent_level)
    return (None, None)

#returns the string of words interpreted from the mic
def recognize_voice(r, m):
    while (True):
        
        print("listening")
        with m as source:
            audio = r.listen(source)
                                
        print("recognizing")        
        while (True):
            try:
                raw_text = r.recognize_google(audio)
                return raw_text
            except TimeoutError:
                print("timed out. trying again")

            except sr.RequestError as e:
                print("request error: {}".format(e))
                print("trying again")
            except sr.UnknownValueError:
                print("could not recognize audio. try speaking again")
                break
    

def main():
    #change this to enable/disable using the mic or entering words
    use_mic = False

    if (use_mic):
        
        r = sr.Recognizer()
        m = sr.Microphone()
        
        print("be silent")
        with m as source:
            #r.adjust_for_ambient_noise(source, 2)
            r.adjust_for_ambient_noise(source)
            r.dynamic_energy_threshold = False
            print("minimum energy threshold: {}".format(r.energy_threshold))
            
    indent_level = 0
    replacements_plus_indent = read_replacements_plus_indent()

    file = open("out.py", "w")

    try:
        while (True):
            
            if (use_mic):
                raw_phrases = recognize_voice(r, m)
            else:
                raw_phrases = input("> ")

            raw_phrases = raw_phrases.lower()
            print("raw_phrases:", raw_phrases)
            
            phrases = raw_phrases.lower().split(" then ")

            for phrase in phrases:
                
                if (phrase == "end program"):
                    print("program finished")
                    return
                
                if (phrase == "end block"):
                    indent_level = max(indent_level-1, 0)
                    continue

                (converted_code, indent_change) = convert_to_code_plus_indent(phrase, replacements_plus_indent)
                    
                print("converted_code:", converted_code)
                        
                if converted_code != None:
                    #print("indent level:", indent_level)
                    file.write(("\t"*indent_level) + converted_code + "\n")
                    #file.flush()
                    indent_level+=indent_change
            


                
    except KeyboardInterrupt:
        print("program terminated")
    finally:
        file.close()

if __name__ == "__main__":
    main()
    
