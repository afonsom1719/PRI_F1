import { ChangeEvent, useState } from "react";
import { Stack, TextField } from "@fluentui/react";
import { Send28Filled } from "@fluentui/react-icons";
import { MicOff28Filled, Mic28Filled } from "@fluentui/react-icons";
import Dropdown from "../LanguageOptions/LanguageOptions";

import { FileUpload } from "../FileUpload/FileUpload";

import styles from "./QuestionInput.module.css";

import * as sdk from "microsoft-cognitiveservices-speech-sdk";
import { SentimentViewer } from "../SentimentViewer";

const SPEECH_KEY = import.meta.env.VITE_SPEECH_KEY;
const SPEECH_REGION = import.meta.env.VITE_SPEECH_REGION;

const speechConfig: sdk.SpeechConfig = sdk.SpeechConfig.fromEndpoint(
    new URL(`wss://${SPEECH_REGION}.stt.speech.microsoft.com/speech/universal/v2`),
    SPEECH_KEY
);

//speechConfig.speechRecognitionLanguage = "en-US";

// let newLanguage = "en-US";

const audioConfig = sdk.AudioConfig.fromDefaultMicrophoneInput();
const autoDetectSourceLanguageConfig = sdk.AutoDetectSourceLanguageConfig.fromLanguages([
    "ar-AE",
    "ar-BH",
    "ar-EG",
    "ar-IQ",
    "ar-JO",
    "ar-KW",
    "ar-LB",
    "ar-OM",
    "ar-QA",
    "ar-SA",
    "ar-SY",
    "ar-YE"
]);
const recognizer = sdk.SpeechRecognizer.FromConfig(speechConfig, autoDetectSourceLanguageConfig, audioConfig);

interface Props {
    onSend: (question: string) => void;
    onFileUpload?: (e: ChangeEvent<HTMLInputElement>) => Promise<void>;
    disabled: boolean;
    placeholder?: string;
    clearOnSend?: boolean;
    sentiment: number;
    handleCallback: (value: string) => void;
}

const MIC_STATUS = {
    recording: "recording",
    stopped: "stop"
};

export const QuestionInput = ({ onSend, disabled, placeholder, clearOnSend, onFileUpload, handleCallback, sentiment }: Props) => {
    const [question, setQuestion] = useState<string>("");
    const [microphoneStatus, setMicrophoneStatus] = useState<string>(MIC_STATUS.stopped);
    const [recordingSound, setRecordingSound] = useState<boolean>(false);

    const sendQuestion = () => {
        if (disabled || !question.trim()) {
            return;
        }

        onSend(question);

        if (clearOnSend) {
            setQuestion("");
        }
        stopAudioRecordingStates();
    };

    /**
     * @function stopAudioRecordingStates
     * @description Stops the recognizer instance execution and updates the states related to the microphone logic.
     */
    const stopAudioRecordingStates = () => {
        recognizer.stopContinuousRecognitionAsync(() => {
            setRecordingSound(false);
            setMicrophoneStatus(MIC_STATUS.stopped);
        });
    };

    /**
     * @function sendAudio
     * @description Starts the audio recording and sends it to the MSFT SPEECH API to transform the speech into text.
     * The transformation occurs every time the user finishes a sentence and stops talking a bit.
     * The output text is then added to the current string on the question state value.
     */
    const sendAudio = () => {
        if (disabled) return;
        if (!recordingSound) {
            setRecordingSound(true);
            setMicrophoneStatus(MIC_STATUS.recording);

            console.log(speechConfig.speechRecognitionLanguage);
            console.log(recognizer.properties.getProperty(sdk.PropertyId.SpeechServiceConnection_RecoLanguage));
            recognizer.startContinuousRecognitionAsync(
                () => {
                    console.log("startContinuousRecognitionAsync success");
                },
                e => {
                    console.error("error");
                }
            );

            let resultTemp = question;
            let resultFinal = question;
            recognizer.recognizing = (s, e) => {
                // adding a start tag to the text so we can identify the first one later and replace the string with the recognized one.
                resultTemp += `<start>${e.result.text}`;
                // update the question state with the intermediate result
                setQuestion(`${resultFinal} ${e.result.text}`);
            };

            recognizer.recognized = (s, e) => {
                if (e.result.text) {
                    // append the final result to the question state and removes the recognizing text from the first start tag.
                    resultTemp = `${resultTemp.split("<start>")[0]} ${e.result.text}`;
                    resultFinal = resultTemp;
                    setQuestion(resultTemp);
                }
            };
            return;
        }

        stopAudioRecordingStates();
    };

    const onEnterPress = (ev: React.KeyboardEvent<Element>) => {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            sendQuestion();
        }
    };

    const onQuestionChange = (_ev: React.FormEvent<HTMLInputElement | HTMLTextAreaElement>, newValue?: string) => {
        if (!newValue) {
            setQuestion("");
        } else if (newValue.length <= 1000) {
            setQuestion(newValue);
        }
    };

    const sendQuestionDisabled = disabled || !question.trim();

    return (
        <>
            <Stack className={styles.questionInputContainer}>
                <Stack horizontal className={`${styles.spaceBetweenElements}`}>
                    {/* <div style={{ display: "flex" }}> */}
                        {/* <Dropdown options={languages} codes={codes} onSelect={handleSelect} label="Choose a language" /> */}
                        {/* <div
                            className={`${styles.questionInputSendButton} ${styles.centerElements}`}
                            aria-label="Audio"
                            role="button"
                            title={microphoneStatus === MIC_STATUS.stopped ? "Start recording" : "Stop Recording"}
                            onClick={sendAudio}
                        >
                            {microphoneStatus === MIC_STATUS.stopped ? (
                                <MicOff28Filled primaryFill="rgba(128, 128, 128, 1)" />
                            ) : (
                                <Mic28Filled
                                    primaryFill="rgba(0, 255, 0, 1)"
                                    className={`${sendQuestionDisabled ? styles.questionInputSendButtonDisabled : ""} ${styles.centerElements}`}
                                />
                            )}
                        </div>
                    </div>
                    <SentimentViewer number={sentiment} /> */}
                </Stack>
                <Stack horizontal className={`${styles.marginTop}`}>
                    <TextField
                        className={styles.questionInputTextArea}
                        placeholder={placeholder}
                        multiline
                        resizable={false}
                        borderless
                        value={question}
                        onChange={onQuestionChange}
                        onKeyDown={onEnterPress}
                    />
                    <div className={styles.questionInputButtonsContainer}>
                        <div
                            className={`${styles.questionInputSendButton} ${sendQuestionDisabled ? styles.questionInputSendButtonDisabled : ""}`}
                            aria-label="Ask question button"
                            role="button"
                            onClick={sendQuestion}
                        >
                            <Send28Filled primaryFill="rgba(115, 118, 225, 1)" />
                        </div>
                    </div>
                </Stack>
            </Stack>
        </>
    );
};
