import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IEditorLanguageRegistry } from '@jupyterlab/codemirror';
import { LabIcon } from '@jupyterlab/ui-components';
import { StreamLanguage, LanguageSupport } from '@codemirror/language';
import { makefile } from './makefile-mode';

// Import SVG icon as string - bold capital M like VS Code
const makefileIconStr = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <text x="12" y="18" font-size="20" font-weight="900" text-anchor="middle" fill="#d84a4a" font-family="Arial, sans-serif">M</text>
</svg>`;

export const makefileIcon = new LabIcon({
  name: 'makefile:icon',
  svgstr: makefileIconStr
});

/**
 * Initialization data for the jupyterlab_makefile_file_type_extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab_makefile_file_type_extension:plugin',
  description:
    'Jupyterlab extension to add handling of Makefiles and syntax colouring support',
  autoStart: true,
  requires: [IEditorLanguageRegistry],
  activate: (app: JupyterFrontEnd, languages: IEditorLanguageRegistry) => {
    console.log(
      'JupyterLab extension jupyterlab_makefile_file_type_extension is activated!'
    );

    // Register Makefile language support
    languages.addLanguage({
      name: 'makefile',
      displayName: 'Makefile',
      mime: 'text/x-makefile',
      extensions: ['.mk'],
      filename: /^(Makefile|makefile|GNUmakefile)$/,
      support: new LanguageSupport(StreamLanguage.define(makefile))
    });

    // Register icon for Makefile file type
    app.docRegistry.addFileType(
      {
        name: 'makefile',
        displayName: 'Makefile',
        mimeTypes: ['text/x-makefile'],
        extensions: ['.mk'],
        pattern: '^(Makefile|makefile|GNUmakefile)$',
        fileFormat: 'text',
        icon: makefileIcon
      },
      ['text/x-makefile']
    );
  }
};

export default plugin;
