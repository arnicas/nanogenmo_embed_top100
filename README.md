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

## Samples 

The start:

```
Once upon a time, in a faraway land...

        --narrator, nanogenmo, distance:0.000, code:input

There—for with your leave, my sister, I will put some trust in preceding navigators—there snow and frost are banished; and, sailing over a calm sea, we may be wafted to a land surpassing in wonders and in beauty every region hitherto discovered on the habitable globe.

        --Shelley, Mary Wollstonecraft, Frankenstein; Or, The Modern Prometheus, distance:0.502, code:start
        
It went with me on my sea-shore walks, and rambles into the country, whenever—which was seldom and reluctantly—I bestirred myself to seek that invigorating charm of Nature, which used to give me such freshness and activity of thought the moment that I stepped across the threshold of the Old Manse.

        --Hawthorne, Nathaniel, The Scarlet Letter, distance:0.503, code:start

At last, after rambling several days about the country, during which the fields afforded me the same bed and the same food which nature bestows on our savage brothers of the creation, I at length arrived at this place, where the solitude and wildness of the country invited me to fix my abode.

        --Fielding, Henry, History of Tom Jones, a Foundling, distance:0.510, code:start

Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world.

      --Melville, Herman, Moby Dick; Or, The Whale, distance:0.514, code:start
```


The end shows the weight of the happily ever after -- almost all Grimm Brothers after the first fortuitous match on Little Women.

```
There they found their child, now grown up to be comely and fair; and after all their troubles they lived happily together to the end of their days.

        --Grimm, Jacob, Grimm, Wilhelm, Grimms' Fairy Tales, distance:0.339, code:end

And then the prince and Briar Rose were married, and the wedding feast was given; and they lived happily together all their lives long.

        --Grimm, Jacob, Grimm, Wilhelm, Grimms' Fairy Tales, distance:0.335, code:end

They were very happy, even after they discovered that they couldn't live on love alone.

        --Alcott, Louisa May, Little Women, distance:0.313, code:end

And they lived happily ever after.
        --narrator, nanogenmo, distance:0.000, code:input
```

The interpolation part finally steers it away from Henry Fielding (which solidly ends the "start" part due to Mr Allworthy)

```
For such was the compassion which inhabited Mr Allworthy's mind, that nothing but the steel of justice could ever subdue it.

        --Fielding, Henry, History of Tom Jones, a Foundling, distance:0.395, code:interp_3

Yet the force of truth did of itself flash into mine eyes, and I turned away my panting soul from incorporeal substance to lineaments, and colours, and bulky magnitudes.

        --Augustine, Saint, Bishop of Hippo, The Confessions of St. Augustine, distance:0.237, code:interp_4

All the truth of my position came flashing on me; and its disappointments, dangers, disgraces, consequences of all kinds, rushed in in such a multitude that I was borne down by them and had to struggle for every breath I drew.

        --Dickens, Charles, Great Expectations, distance:0.380, code:interp_5
```

## Issues

I don't like the top 100 list :) I had no idea there would be so much non-fiction in there, but I suppose I should expect Nietzsche and the Bible. I would prefer to do it with top 100 fiction only, and maybe more writers I like.

After looking at the output, I think it needs some visualization elements (distance between, tallies of writers that showed up most) and some reasoning to handle proper nouns better (strip them out before embedding), but deadline. There is logic to prevent repeated sentence use, but not repeated book use, and there's a whole segment from one Fielding book near the middle.  This is due to proper nouns biasing the search.

I missed a few cleaning rules, like initial numbers.

More structure would help the story, too but I wanted to do something simple.

## Code files

All the code parts (not the data) are here, mix of scripts and notebooks, but I will clean them up and document in mid-December.



