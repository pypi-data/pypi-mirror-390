import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';

/**
 * Initialization data for the jupyter-ra-extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter-ra-extension:plugin',
  description: 'Relational Algebra Symbols in Jupyter Lab',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, tracker: INotebookTracker) => {
    // send start message
    console.log('JupyterLab extension jupyter-ra-extension is activated!');

    // define helper functions
    const insertText = (text: string) => {
      const current = tracker.currentWidget;
      const notebook = current!.content;
      const activeCell = notebook.activeCell;

      activeCell!.editor!.replaceSelection!(text);
    };

    // register commands
    app.commands.addCommand('ratui:text1', {
      label: 'RA:',
      caption: 'Relational Algebra',
      isEnabled: () => false,
      execute: () => {}
    });

    app.commands.addCommand('ratui:projection', {
      label: 'π',
      caption: 'Projection:\nπ [a, b] (R)\nAlternative: pi',
      execute: () => insertText('π')
    });
    app.commands.addCommand('ratui:selection', {
      label: 'σ',
      caption: 'Selection:\nσ [a=1] (R)\nAlternative: sigma',
      execute: () => insertText('σ')
    });
    app.commands.addCommand('ratui:attributerename', {
      label: 'β',
      caption: 'Rename Attribute:\nβ [a←b] (R)\nAlternative: beta',
      execute: () => insertText('β')
    });
    app.commands.addCommand('ratui:rename', {
      label: 'ρ',
      caption: 'Rename:\nρ [ S(A, B, C) ] (R)\nAlternative: rho',
      execute: () => insertText('ρ')
    });
    app.commands.addCommand('ratui:cross', {
      label: '×',
      caption: 'Cross Product:\nR × S\nAlternative: times',
      execute: () => insertText('×')
    });
    app.commands.addCommand('ratui:join', {
      label: '⋈',
      caption: 'Natural Join:\nR ⋈ S\nAlternative: join',
      execute: () => insertText('⋈')
    });
    app.commands.addCommand('ratui:left-outer-join', {
      label: '⟕',
      caption: 'Left Outer Join:\nR ⟕ S\nAlternative: ljoin',
      execute: () => insertText('⟕')
    });
    app.commands.addCommand('ratui:right-outer-join', {
      label: '⟖',
      caption: 'Right Outer Join:\nR ⟖ S\nAlternative: rjoin',
      execute: () => insertText('⟖')
    });
    app.commands.addCommand('ratui:full-outer-join', {
      label: '⟗',
      caption: 'Full Outer Join:\nR ⟗ S\nAlternative: fjoin, ojoin',
      execute: () => insertText('⟗')
    });
    app.commands.addCommand('ratui:left-semi-join', {
      label: '⋉',
      caption: 'Left Semi Join:\nR ⋉ S\nAlternative: lsjoin',
      execute: () => insertText('⋉')
    });
    app.commands.addCommand('ratui:right-semi-join', {
      label: '⋊',
      caption: 'Right Semi Join:\nR ⋊ S\nAlternative: rsjoin',
      execute: () => insertText('⋊')
    });
    app.commands.addCommand('ratui:union', {
      label: '∪',
      caption: 'Union:\nR ∪ S\nAlternative: cup',
      execute: () => insertText('∪')
    });
    app.commands.addCommand('ratui:intersection', {
      label: '∩',
      caption: 'Intersect:\nR ∩ S\nAlternative: cap',
      execute: () => insertText('∩')
    });
    app.commands.addCommand('ratui:difference', {
      label: '-',
      caption: 'Difference:\nR - S\nAlternative: \\',
      execute: () => insertText('-')
    });
    app.commands.addCommand('ratui:division', {
      label: '÷',
      caption: 'Division:\nR ÷ S\nAlternative: :',
      execute: () => insertText('÷')
    });

    app.commands.addCommand('ratui:text2', {
      label: '|',
      isEnabled: () => false,
      execute: () => {}
    });

    app.commands.addCommand('ratui:arrowleft', {
      label: '←',
      caption: 'Alternative: <-',
      execute: () => insertText('←')
    });

    app.commands.addCommand('ratui:text3', {
      label: '|',
      isEnabled: () => false,
      execute: () => {}
    });

    app.commands.addCommand('ratui:and', {
      label: '∧',
      caption: 'Alternative: and',
      execute: () => insertText('∧')
    });
    app.commands.addCommand('ratui:or', {
      label: '∨',
      caption: 'Alternative: or',
      execute: () => insertText('∨')
    });
    app.commands.addCommand('ratui:not', {
      label: '¬',
      caption: 'Alternative: !',
      execute: () => insertText('¬')
    });

    app.commands.addCommand('ratui:text4', {
      label: '|',
      isEnabled: () => false,
      execute: () => {}
    });

    app.commands.addCommand('ratui:equal', {
      label: '=',
      execute: () => insertText('=')
    });
    app.commands.addCommand('ratui:unequal', {
      label: '≠',
      caption: 'Alternative: !=',
      execute: () => insertText('≠')
    });
    app.commands.addCommand('ratui:lt', {
      label: '<',
      execute: () => insertText('<')
    });
    app.commands.addCommand('ratui:lte', {
      label: '≤',
      caption: 'Alternative: <=',
      execute: () => insertText('≤')
    });
    app.commands.addCommand('ratui:gte', {
      label: '≥',
      caption: 'Alternative: >=',
      execute: () => insertText('≥')
    });
    app.commands.addCommand('ratui:gt', {
      label: '>',
      execute: () => insertText('>')
    });
  }
};

export default plugin;
