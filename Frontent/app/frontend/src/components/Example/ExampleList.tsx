import { Example } from "./Example";

import styles from "./Example.module.css";

export type ExampleModel = {
    text: string;
    value: string;
};

const EXAMPLES: ExampleModel[] = [
    {
        text: "What was the fastest lap time for driver Charles Leclerc at the 2018 occurrence of the Australian Grand Prix?",
        value: "What was the fastest lap time for driver Charles Leclerc at the 2018 occurrence of the Australian Grand Prix?"
    },
    {
        text: "Give me 4 circuits located in Italy.",
        value: "Give me 4 circuits located in Italy."
    },
    {
        text: "Which was the time of the fastest pitstop at the 2021 Portuguese Grand Prix?",
        value: "Which was the time of the fastest pitstop at the 2021 Portuguese Grand Prix?"
    },
    {
        text: "Name some drivers with the surname Schumacher.",
        value: "Name some drivers with the surname Schumacher."
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
