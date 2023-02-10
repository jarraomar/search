Names: Jarra Omar and Orlando Cedeno

Known Bugs: The list returned from the query for page rank returns all the right pages but in the wrong order

User interaction: A user should be mindful of how the index class is set up where the parameters of the class 
follows self,wiki,titles,docs,words. From there, all of the information needed can be accessed through the 
global dictionaries once any helper functions or filler functions have been applied. It can also be changed, for example
if the delta or epsilon value needs to be changed and it can be done so within a swift matter 

How pieces fit together: Individual components of the code handled the filling of major dicitonaries so that the large wikis 
wouldn't have to be read every single time. After processing words within the wiki (parsing,stemming,etc), we filled in the dictionaries 
which would then be accessed to further fill different dictionaries. For example, the id to titles dictionary was used to help fill in the 
word to freq dictionaries which would then be vital for calculating the relevances. They all come full circle and by breaking it down, it 
helps contextualize the code and environment we're working with.

Description of features we failed to implement: Catching possible user inputs that may not be present or isn't valid for the search we're doing
Small exceptions that wouldn't be harmful unless ran into. Small nuiances we missed but overall wasn't dentrimental to the code.

Description of how we tested the code:
    Tested id to titles and titles to id with a small wiki and created a small dictionary to see if it mapped them correctly
    Tested the is link helper function to see if it identified whether a link was a link or not
    Tested split by asserting if the results it produced we're what they have should've been, similar to the examples given in the handout
    Tested relevance by making a wiki almost exactly like the one found in the handout, except we switched the word out for the to theater
    since "the" would be a stopped word and wouldn't have been added to the dictionary
    Tested page rank by just checking to see if the sum of the page rank values = 1




