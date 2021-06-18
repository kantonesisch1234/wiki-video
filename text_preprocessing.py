import re

# A method that adds new line to a text, where each line has a maximum number of chars 
# and a new line is added only between words

def bend(s, w):
    s = s.split(" ") #creates list of all the words (any sequence between characters)
    lst = filter(None, s) # removes the repeated spaces from list
    new_lst = [""]
    i = 0
    for word in lst:
        line = new_lst[i] + " " + word #possible line
        if(new_lst[i] == ""): #first time is different
            line = word
        if(len(word)  > w): #splits words that are too large
            while(len(word)  > w):
                new_lst.append(word[:w])
                i += 1
                word = word[w:]
            i += 1
            new_lst.append(word)
        elif(len(line) > w):
            new_lst.append(word) #line length reached, start new line
            i += 1        
        else:
            new_lst[i] = line
    return "\n".join(new_lst) #insert new line characters

def seperate_string_every_n_lines(s, n):
    s_list = s.split('\n')
    tmp_str = ''
    str_list = []
    tmp_str = ''
    for idx, line in enumerate(s_list):
        tmp_str += line+'\n'
        if idx%n == n-1:
            str_list.append(tmp_str.strip('\n'))
            tmp_str = ''
    if tmp_str:
        str_list.append(tmp_str.strip('\n'))
    return str_list


def cut_sentences(content, words_per_line=0, split_middle=True, remove_brackets=True, remove_referencing=True, 
                  remove_quotation_marks=True, remove_punctuations=True, new_line_after_space=False, max_lines = 0):
    
    def remove_brackets_func(string):
        new_string = re.sub("\(.*?\)", "", string)
        new_string = re.sub("（.*?）", "", new_string)
        return new_string
    
    def remove_referencing_func(string):
        return re.sub("\[[0-9]+\]", "",string)
    
    def remove_punctuations_func(string):
        return re.sub("[,\.;，。:：;；!！\?？]", "", string)
    
    def remove_quotation_marks(string):
        return re.sub("[「」『』《》“”‘’\'\"]", "" ,string)
    
    if remove_brackets:
        content = remove_brackets_func(content)
        
    if remove_referencing:
        content = remove_referencing_func(content)
        
    if remove_quotation_marks:
        content = remove_quotation_marks(content)
    
    end_flag =  [ '?' ,  '!' ,  '.' ,  '？' ,  '！' ,  '。' ,  '…' ]
    # middle_flag = [',', '，', ';', '；', ':', '：']
    middle_flag = ['，', ';', '；', ':', '：']
    
    if split_middle:
        end_flag = end_flag + middle_flag

    content = content.strip()
    content_len =  len(content)
    sentences =  []
    tmp_char =  '' 
    for idx, char in enumerate(content):
        
        if char == "\n":
            if sentences[-1] == "\n":
                continue
            else:
                sentences.append(char)
            continue
        
        tmp_char += char
        
        if idx + 1 == content_len: 
            sentences.append(tmp_char)
            break
            
        if char in end_flag:
            next_idx = idx + 1 
            if not content[next_idx] in end_flag:
                sentences.append(tmp_char)
                tmp_char =  ''
    
    if remove_punctuations:
        new_sentences = []
        for sentence in sentences:
            new_sentences.append(remove_punctuations_func(sentence))
        sentences = new_sentences
    
    if words_per_line != 0:
        new_sentences = []
        if not new_line_after_space:
            for sentence in sentences:
                tmp_char = ''
                for idx, char in enumerate(sentence):
                    tmp_char += char
                    if idx % words_per_line == words_per_line-1:
                        tmp_char += '\n'
                new_sentences.append(tmp_char)
            sentences = new_sentences

                
        else:
            for sentence in sentences:
                new_sentences.append(bend(sentence, words_per_line))
            sentences = new_sentences
        if max_lines:
            new_sentences = []
            for sentence in sentences:
                new_sentences += seperate_string_every_n_lines(sentence, max_lines)
            sentences = new_sentences
    return sentences

def get_subtitles_from_textfile(text, lang="zh-tw", words_per_line=0, max_lines=0):
    if lang == "zh-tw":
        sentences = cut_sentences(text, remove_punctuations=True, split_middle=True, words_per_line=words_per_line,
                                 max_lines=max_lines)
    if lang == "ja":
        sentences = cut_sentences(text, remove_punctuations=False, split_middle=True, words_per_line=words_per_line,
                                 max_lines=max_lines)
    elif lang == "de" or lang == "en" or lang == "ru":
        sentences = cut_sentences(text, remove_punctuations=False, remove_quotation_marks=False, split_middle=True, 
                                  new_line_after_space=True, words_per_line=words_per_line, max_lines=max_lines)
    return sentences
    
    
    
    
    