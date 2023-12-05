import { Example } from "./Example";

import styles from "./Example.module.css";

export type ExampleModel = {
    text: string;
    value: string;
};

const EXAMPLES: ExampleModel[] = [
    {
        text: "What is the include weekends setting?",
        value: "What is the include weekends setting?"
    },
    {
        text: "In the video creatives what are the field names on the platform UI when uploading a raw video file?",
        value: "In the video creatives what are the field names on the platform UI when uploading a raw video file?"
    },
    {
        text: "What are the standard targeting options available for selection in the Platform UI?",
        value: "What are the standard targeting options available for selection in the Platform UI?"
    },
    {
        text: "Create an image of a Friendly robot, serving coffee, 3D render",
        value: "Create an image of a Friendly robot, serving coffee, 3D render"
    }
];

interface Props {
    onExampleClicked: (value: string) => void;
}

export const ExampleList = ({ onExampleClicked }: Props) => {
    return (
        <ul className={styles.examplesNavList}>
            {EXAMPLES.map((x, i) => (
                <li key={i}>
                    <Example text={x.text} value={x.value} onClick={onExampleClicked} />
                </li>
            ))}
        </ul>
    );
};
