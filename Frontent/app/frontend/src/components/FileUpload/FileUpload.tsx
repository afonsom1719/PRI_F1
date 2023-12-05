import { ArrowUpload24Filled } from "@fluentui/react-icons";
import React, { useState, useRef, useEffect, ChangeEvent } from "react";
import styles from "../QuestionInput/QuestionInput.module.css";

interface AppProps {
    isDisabled: boolean;
    sendQuestionDisabled: boolean;
    onFileUpload: (e: ChangeEvent<HTMLInputElement>) => Promise<void>;
}

export function FileUpload({ isDisabled, sendQuestionDisabled, onFileUpload }: AppProps) {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const allowedFileTypes = ["image/png", "image/jpeg", "image/jpg", "application/pdf"];

    const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFile(e.target.files[0]);
            await onFileUpload(e);
            setSelectedFile(null);
            fileInputRef.current!.value = "";
        }
    };

    const updateFileName = () => {
        const fileInput = fileInputRef.current;
        const selectedFile = fileInput?.files?.[0];

        if (!selectedFile) return;

        if (!allowedFileTypes.includes(selectedFile.type)) {
            fileInputRef.current!.textContent = "File type not allowed";
        } else {
            fileInputRef.current!.textContent = selectedFile.name;
        }
    };

    useEffect(() => {
        updateFileName();
    }, [selectedFile]);

    const handleAttachClick = () => {
        if (isDisabled) return;
        // Programmatically trigger the file input click event
        fileInputRef.current?.click();
    };

    return (
        <div
            className={`${styles.questionInputSendButton} ${sendQuestionDisabled ? styles.questionInputSendButtonDisabled : ""} ${styles.centerElements}`}
            aria-label="Attach File"
            title={selectedFile ? selectedFile.name : "Attach File"}
            onClick={handleAttachClick}
            role="button"
        >
            {selectedFile ? <ArrowUpload24Filled primaryFill="rgba(0, 255, 0, 1)" /> : <ArrowUpload24Filled primaryFill="rgba(128, 128, 128, 1)" />}

            <input
                type="file"
                ref={fileInputRef}
                style={{ display: "none" }} // Hide the file input element
                accept={allowedFileTypes.join(",")}
                onChange={handleFileChange}
            />
        </div>
    );
}
