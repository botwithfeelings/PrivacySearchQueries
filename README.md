# PrivacySearchQueries: Leveraging Search Query Trends as a Privacy Preference Proxy

## Introduction
In 2015, Pew Research Center published a report discussing how the online activities and habits of American adults have changed since Edward Snowden began leaking documents about government intelligence programs [\[6\]](#ref). Their survey identified how people changed their online behavior as they became aware of surveillance. Of the 87% of respondents who were familiar with the surveillance program, 34% had taken at least one step to hide or shield their information from the government, while 25% had claimed to change their technological patterns of use.

These findings are encouraging as they indicate that revelations of privacy-invasive programs make people change their online behaviors to better protect their sensitive data.
Privacy-related decision-making like this has been actively studied for some time with much of the research focusing on the "privacy paradox" in which behavioral decisions seem at odds with reported preferences (see, for example [\[2, 3\]](#ref)).  Therefore, it is important to verify the results of the Pew report. Since running another large-scale survey would be costly and potentially biased by the paradox, another method of measuring privacy concern is needed to qualify the change in preferences over time.

## Methodology
We identified the main themes of behavioral changes in the Pew Research report as social media settings and privacy, web anonymity, deleting social media accounts, apps and privacy, deleting apps, removing social media connections, and email privacy. As an initial investigatory step, we conducted a survey on Amazon Mechanical Turk (AMT) to determine how individuals might learn more about these topics and how to achieve specified tasks (available options were "ask a friend", "visit a specific website", "read a book about it", "use a search engine", "use something else", and "none of these"). The most common method of finding out more information for each of the topics was to use a search engine
(56%) with Google being the most common one;
the second most common method was to ask a friend (28%).

Based on these results, we chose to use search query trends to construct an index which should provide us with the ability to compare the general population's interest in privacy topics across time. This method has been used in other disciplines for measuring trends in time [\[5\]](#ref) and making predictions [\[4\]](#ref), but has not yet been used to track opinions on technology-related topics.

In order to use search queries as an index, we have laid out the following plan:

* Construct a set of search queries related to the core concepts identified in the Pew Report. (We are currently generating this set with a recursive expansion on an initial seed query by mining Google's related queries.)
* Leverage Google Trends [\[1\]](#ref) to track the temporal popularity of the related queries from before the Snowden revelations up to present time.
* Create an index based on the search query trends to determine if the population's behavior has changed in a manner consistent with the Pew Report's results.

<a name="ref">
## References
[1] [https://www.google.com/trends/](https://www.google.com/trends/)


[2]  A. Acquisti and J. Grossklags.  Privacy and rationality in individual decision making.IEEE Security & Privacy, 2(2005):24–30, 2005.

[3]  S. B. Barnes. A privacy paradox:  Social networkingin the united states.First Monday, 11(9), 2006.

[4] A. F. Dugas, M. Jalalpour, Y. Gel, S. Levin, F. Torcaso, T. Igusa, and R. E. Rothman. Influenza forecasting with google flu trends. PloS one, 8(2):e56176, 2013.

[5] S. Funk and D. Rusowsky. The importance of cultural knowledge and scale for analysing internet search data as a proxy for public interest toward the environment. Biodiversity & Conservation, 23(12): 3101–3112, Nov. 2014.

[6] L. Rainie and M. Madden. Americans' Privacy Strategies Post-Snowden. Technical report, Pew Internet & American Life Project, [http://www.pewinternet.org/2015/03/16/americans-privacy-strategies-post-snowden/](http://www.pewinternet.org/2015/03/16/americans-privacy-strategies-post-snowden/), March 16 2015. Accessed: December 12 2016.
