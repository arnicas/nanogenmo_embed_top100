# NanoGenMo 2024 -- Once Upon a Time/Happily Ever After

A story constructed with sentences from Gutenberg Books using embedding similarity search. 


## Overview

1. Take the top 100 books on Gutenberg Books, filter out the non-english and Victorian porn, and dupes.

2. Then clean them of starter/end material, and clean up or remove sentences (too long, too short, roman numerals, etc.)

3. Embed each sentence using a small embedding model.

4. Put data into a vector database (Chroma).

5. From a start and end sequence:
"Once upon a time, in a land far away..."
and "They lived happily ever after."

6. Search for nearest neighbors. Pick closest sentence, and repeat using each sentence as a new search.

7. Generate half the text.

8. Reverse the order of the ending sentences, so they end with the "Happily Ever After" part.

9. Use interpolation to generate 10 sentences of merger text that starts with the last sentence of 
the first half, and ends with the first sentence of the second half (after reversing their order).

10. Write them all to a markdown file, with the source title, author, distance score, and a code saying which section it is (start, end, interp).

Output is in output.md.

## Issues

After looking at the output, I think it needs some visualization elements and some reasoning to handle proper nouns better, but deadline. There is logic to prevent repeated sentence use, but not repeated book use, and there's a whole segment from one book near the middle.  This is due to proper nouns biasing the search.  More structure would help the story, too.

## Code files

All the code parts (not the data) are here, mix of scripts and notebooks, but I will clean them up in mid-December.



