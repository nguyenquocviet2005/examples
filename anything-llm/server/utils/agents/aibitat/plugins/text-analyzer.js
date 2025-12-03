const { Deduplicator } = require("../utils/dedupe");

/**
 * Text Analyzer Skill
 * 
 * This is an example agent skill that performs text analysis operations.
 * It demonstrates key skill patterns:
 * - Function definition with description and parameters
 * - JSON Schema for input validation
 * - Examples for LLM few-shot learning
 * - Handler function execution
 * - Deduplication to prevent duplicate calls
 * - Communication back to the user via socket
 */
const textAnalyzer = {
  name: "text-analyzer",
  startupConfig: {
    params: {},
  },
  plugin: function () {
    return {
      name: this.name,
      setup(aibitat) {
        aibitat.function({
          super: aibitat,
          tracker: new Deduplicator(),
          name: this.name,
          
          // Description tells the LLM when/why to use this skill
          description:
            "Analyze text to extract statistics, sentiment, keywords, and other metrics. Useful for understanding content at a glance.",
          
          // Examples help the LLM understand how to call this function
          examples: [
            {
              prompt: "What are the most common words in this text?",
              call: JSON.stringify({
                text: "the text provided by user",
                analysis_type: "keywords",
              }),
            },
            {
              prompt: "Analyze the sentiment of this paragraph",
              call: JSON.stringify({
                text: "the text provided by user",
                analysis_type: "sentiment",
              }),
            },
            {
              prompt: "Count the words and sentences",
              call: JSON.stringify({
                text: "the text provided by user",
                analysis_type: "statistics",
              }),
            },
          ],
          
          // Parameters define what inputs the function accepts (JSON Schema)
          parameters: {
            $schema: "http://json-schema.org/draft-07/schema#",
            type: "object",
            properties: {
              text: {
                type: "string",
                description: "The text content to analyze.",
              },
              analysis_type: {
                type: "string",
                enum: ["keywords", "sentiment", "statistics", "readability"],
                description:
                  "Type of analysis to perform: keywords (extract top words), sentiment (positive/negative/neutral), statistics (word/sentence count), or readability (flesch-kincaid grade).",
              },
            },
            additionalProperties: false,
          },
          required: ["text", "analysis_type"],
          
          // Handler is the main function that executes the skill
          handler: async function ({ text = "", analysis_type = "keywords" }) {
            try {
              // Check for duplicate calls to prevent redundant analysis
              if (
                this.tracker.isDuplicate(this.name, { text, analysis_type })
              ) {
                this.super.handlerProps.log(
                  `${this.name} was called with duplicate parameters, skipping.`
                );
                return "This text has already been analyzed. The results are shown above.";
              }

              let result;

              // Route to appropriate analysis function
              switch (analysis_type) {
                case "keywords":
                  result = await this.analyzeKeywords(text);
                  break;
                case "sentiment":
                  result = await this.analyzeSentiment(text);
                  break;
                case "statistics":
                  result = await this.analyzeStatistics(text);
                  break;
                case "readability":
                  result = await this.analyzeReadability(text);
                  break;
                default:
                  return "Invalid analysis type specified.";
              }

              // Log the action for debugging
              this.super.introspect(
                `${this.caller}: Analyzing text for ${analysis_type}.`
              );

              // Track that we've performed this analysis
              this.tracker.trackRun(this.name, { text, analysis_type });

              return result;
            } catch (error) {
              this.super.handlerProps.log(
                `text-analyzer raised an error: ${error.message}`
              );
              return `An error occurred while analyzing the text: ${error.message}`;
            }
          },

          /**
           * Extract and rank keywords from text
           */
          analyzeKeywords: async function (text) {
            const words = text
              .toLowerCase()
              .match(/\b[\w]+\b/g) || [];
            const commonWords = new Set([
              "the",
              "a",
              "an",
              "and",
              "or",
              "but",
              "in",
              "on",
              "at",
              "to",
              "for",
              "of",
              "with",
              "is",
              "are",
              "was",
              "were",
              "be",
              "been",
            ]);

            // Filter out common words and count frequency
            const wordFreq = {};
            words
              .filter((word) => !commonWords.has(word) && word.length > 3)
              .forEach((word) => {
                wordFreq[word] = (wordFreq[word] || 0) + 1;
              });

            // Sort by frequency
            const topKeywords = Object.entries(wordFreq)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 10)
              .map(([word, count]) => `${word} (${count})`);

            return `**Top Keywords:** ${topKeywords.join(", ")}`;
          },

          /**
           * Simple sentiment analysis
           */
          analyzeSentiment: async function (text) {
            const positiveWords = new Set([
              "good",
              "great",
              "excellent",
              "amazing",
              "wonderful",
              "fantastic",
              "love",
              "best",
              "happy",
              "perfect",
            ]);
            const negativeWords = new Set([
              "bad",
              "terrible",
              "awful",
              "horrible",
              "worst",
              "hate",
              "disappointing",
              "sad",
              "angry",
              "poor",
            ]);

            const lowerText = text.toLowerCase();
            let positiveCount = 0;
            let negativeCount = 0;

            positiveWords.forEach((word) => {
              positiveCount += (lowerText.match(new RegExp(word, "g")) || [])
                .length;
            });

            negativeWords.forEach((word) => {
              negativeCount += (lowerText.match(new RegExp(word, "g")) || [])
                .length;
            });

            let sentiment = "Neutral";
            if (positiveCount > negativeCount) {
              sentiment = "Positive";
            } else if (negativeCount > positiveCount) {
              sentiment = "Negative";
            }

            return `**Sentiment:** ${sentiment} (Positive: ${positiveCount}, Negative: ${negativeCount})`;
          },

          /**
           * Calculate basic text statistics
           */
          analyzeStatistics: async function (text) {
            const words = (text.match(/\b[\w]+\b/g) || []).length;
            const sentences = (text.match(/[.!?]+/g) || []).length || 1;
            const characters = text.length;
            const charactersNoSpaces = text.replace(/\s/g, "").length;
            const avgWordLength = (charactersNoSpaces / words).toFixed(1);
            const avgWordsPerSentence = (words / sentences).toFixed(1);

            return `**Text Statistics:**
- Words: ${words}
- Sentences: ${sentences}
- Characters: ${characters}
- Characters (no spaces): ${charactersNoSpaces}
- Avg word length: ${avgWordLength}
- Avg words per sentence: ${avgWordsPerSentence}`;
          },

          /**
           * Calculate Flesch-Kincaid Grade Level
           */
          analyzeReadability: async function (text) {
            const words = (text.match(/\b[\w]+\b/g) || []).length;
            const sentences = (text.match(/[.!?]+/g) || []).length || 1;
            const syllables = this.countSyllables(text);

            // Flesch-Kincaid Grade Level formula
            const grade =
              (0.39 * words) / sentences +
              (11.8 * syllables) / words -
              15.59;
            const gradeLevel = Math.max(0, grade.toFixed(1));

            let readabilityLevel = "Very Easy (5th grade)";
            if (gradeLevel < 6) readabilityLevel = "Very Easy (5th grade)";
            else if (gradeLevel < 9) readabilityLevel = "Easy (6th-8th grade)";
            else if (gradeLevel < 13)
              readabilityLevel = "Average (9th-12th grade)";
            else if (gradeLevel < 16) readabilityLevel = "Difficult (College)";
            else readabilityLevel = "Very Difficult (Graduate)";

            return `**Readability Analysis:**
- Grade Level: ${gradeLevel}
- Level: ${readabilityLevel}
- Syllables: ${syllables}`;
          },

          /**
           * Simple syllable counter (approximation)
           */
          countSyllables: function (text) {
            const words = (text.match(/\b[\w]+\b/g) || []).map((w) =>
              w.toLowerCase()
            );
            let syllableCount = 0;

            words.forEach((word) => {
              syllableCount += Math.max(
                1,
                (word.match(/[aeiouy]/g) || []).length
              );
            });

            return syllableCount;
          },
        });
      },
    };
  },
};

module.exports = {
  textAnalyzer,
};
