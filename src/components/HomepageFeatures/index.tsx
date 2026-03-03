import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Link from '@docusaurus/Link';
import DocsSvg from '@site/static/img/docs-image.svg';

function Feature() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <DocsSvg
          className={styles.featureSvg}
          role="img"
        />
      </div>
      <div className="text--center padding-horiz--md">
        <Link to={siteConfig.baseUrl + 'docs'}>
          <Heading as="h3">Documentation</Heading>
        </Link>
        <p>Learn how to use the app.</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
            <Feature />
        </div>
      </div>
    </section>
  );
}
