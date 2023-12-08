import { Outlet, NavLink, Link } from "react-router-dom";

import github from "../../assets/github.svg";
import ReactCountryFlag from "react-country-flag";
import Dropdown from "../../components/LanguageOptions/LanguageOptions";
import styles from "./Layout.module.css";

const Layout = () => {
    return (
        <div className={styles.layout}>
            <header className={styles.header} role={"banner"}>
                <div className={styles.headerContainer}>
                    <Link to="/" className={styles.headerTitleContainer}>
                        <h3 className={`${styles.headerTitle} ${styles.armisHeaderH3}`}>Formula GPT</h3>
                    </Link>
                    <nav>
                        <ul className={styles.headerNavList}>
                            <li className={`${styles.armisHeaderLi}`}>
                                <NavLink to="/" className={({ isActive }) => (isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink)}>
                                    Chat
                                </NavLink>
                            </li>
                        </ul>
                    </nav>
                    <h3 className={`${styles.headerRightText} ${styles.armisHeaderH3}`}>FEUP PRI</h3>
                </div>
            </header>

            <Outlet />
        </div>
    );
};

export default Layout;
