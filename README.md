# Stat2Card
🏀 Turns real NBA player stats into 2K-style player cards using machine learning.

For background, NBA 2K is a basketball game where players are rated based on their real-life performance. Stat2Card predicts these ratings using real NBA stats and machine learning.

# The Process

## Obtaining Data
- To obtain the real-life player stat data, we will extract data from websites like `basketball-reference`
- To obtain NBA 2k card ratings we can similary extract the data from popular websites like `www.nba2klab.com` and `2kratings.com`

## Training 
To get the most accurate results, training will be sectioned into different phases based on stat type.

For example, if we are training for defensive stat predictions then the input will only include defensive statistics and height. By doing this, any noise from other non-related stats is completely removed.

## The rest
Work in progress 🏗️
