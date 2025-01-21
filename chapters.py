import re
from pprint import pprint

chapter_ranges = [
    # Chapter 1 -10
    (5, 18),
    (18, 33),
    (33, 42),
    (42, 59),
    (59, 74),
    (74, 94),
    (94, 112),
    (112, 130),
    (130, 149),
    (149, 156),
    # Chapter 11 - 15
    (156, 170),
    (170, 185),
    (185, 203),
    (203, 235),
    (235, 261),
]


chapters = [""] * 15

# For every chaapter range
for chapter_index, chapter_range in enumerate(chapter_ranges):
    # Look at each page
    for page_index in range(chapter_range[0], chapter_range[1]):
        # Extract the text and store the text
        with open(f"text_from_images/page_{page_index}.txt") as f:
            text = f.read()
            chapters[chapter_index] += text

    # Remove all new line characters from the text
    chapters[chapter_index] = re.sub(r"(?<!\n)\n(?!\n)", " ", chapters[chapter_index])
    # Split the chapters into paragraphs
    chapters[chapter_index] = chapters[chapter_index].split("\n\n")
    # Remove the title of the chapter
    del chapters[chapter_index][0]


# The output is an array of arrays
# An array of chapters where each chapter is an array of paragraphs



# This code below is to look at a sample of how the chapters look like
# for i in range(0, 2):
#     print(i)
#     print("=" * 50)
#     pprint(chapters[i][:2])
