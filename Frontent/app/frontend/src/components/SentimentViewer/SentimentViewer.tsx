import React from "react";
import InputEmoji from "react-input-emoji";

// A type for the props of the SentimentViewer component
type SentimentViewerProps = {
    // A number from 1 to 10
    number: number;
};

// A function that returns a color based on a number from 1 to 10
// The lower the number, the redder the color
// The higher the number, the greener the color
const getEmoji = (number: number) => {
    // A list of colors from red to green
    const colors = [0x1f614, 0x1f613, 0x1f612, 0x1f612, 0x1f60a, 0x1f609, 0x1f609, 0x1f600, 0x1f60e, 0x1f600];
    // Return the color corresponding to the number
    return colors[number - 1];
};

// A component that renders a bar that is filled based on a number from 1 to 10
export const SentimentViewer: React.FC<SentimentViewerProps> = ({ number }) => {
    // Get the emoji for the number
    const emoji = getEmoji(number);
    return (
        <div>
            <span title={`Sentiment: ${number}/10`}>{String.fromCodePoint(emoji)}</span>
        </div>
    );
};
