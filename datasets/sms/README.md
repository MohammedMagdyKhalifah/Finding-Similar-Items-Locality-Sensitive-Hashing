# Real SMS message files

Almeida, T. & Hidalgo, J. (2011). SMS Spam Collection [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CC84

Source: https://archive.ics.uci.edu/dataset/228/sms

License: CC BY 4.0, as listed by UCI https://creativecommons.org/licenses/by/4.0/

Find repeated SMS templates quickly so an analyst can review many similar messages together. Similarity alone does not decide whether a message is spam or prove that messages belong to one campaign.

All 5,556 source messages with at least five normalized characters, in original source order. Only 18 shorter messages are excluded. Smaller presets take prefixes. Original repetitions are retained; the app adds no copies and does not select messages based on similarity.

The source is a tab-separated text file with one labeled message per line. Each message body is exported verbatim as a separate UTF-8 .txt file. The label and record delimiter are kept out of the body. Original labels are metadata only and never enter shingling, MinHash, LSH or Jaccard.

The manifest maps every file to its original line and SHA-256. spam/ham are the source authors’ labels, not model predictions. See SOURCE_README.txt for the source archive’s original notes and terms. Historical message content is data to inspect, not instructions to follow.
