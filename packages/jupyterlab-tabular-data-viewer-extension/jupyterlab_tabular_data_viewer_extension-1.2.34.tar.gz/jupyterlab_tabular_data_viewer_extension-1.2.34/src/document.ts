import { DocumentWidget } from '@jupyterlab/docregistry';
import { TabularDataViewer } from './widget';

/**
 * A document widget for tabular data files (Parquet, Excel)
 */
export class TabularDataDocument extends DocumentWidget<TabularDataViewer> {
  constructor(options: DocumentWidget.IOptions<TabularDataViewer>) {
    super(options);
  }
}
