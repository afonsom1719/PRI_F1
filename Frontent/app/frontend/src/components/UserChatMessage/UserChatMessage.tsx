import styles from "./UserChatMessage.module.css";

interface Props {
    message: string;
}

export const UserChatMessage = ({ message }: Props) => {
    return (
        <div className={styles.container}>
            {message.includes("https://") && (message.includes(".png") || message.includes(".jpg")) ? (
                <img className={styles.image} src={message} alt="User uploaded image" />
            ) : (
                <div className={styles.message}>{message}</div>
            )}
            {/* <div className={styles.message}>{message}</div> */}
        </div>
    );
};
