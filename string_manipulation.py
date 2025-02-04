
text = ''

with open("output/sample.txt", "r") as f:
    text = f.read()
f.close()

print(len(text))
text = text.split("Contact Information")[0].replace('\n', ' ')
'''
to avoid issues when checking a number, i am removing all ',' or '.' when reading
the text
'''

list = []
text = text.split(" ")
r = len(text)
print(r)
cur = 0
start = 0
end = 0
found = False
distance = 5

while cur < r:
    if found:
        if text[cur].replace(",", "").isdigit():
            end = cur
        elif cur - end > distance:
            found = False
            list.append(" ".join(text[max(start - distance, 0) : cur]))
    else:
        if text[cur].replace(",", "").isdigit():
            start = cur
            end = cur
            found = True
    cur += 1

word_length = 0
for m in list:
    word_length += len(m.split(" "))
    # print(m)
print(word_length)