import {JupyterFrontEnd, JupyterFrontEndPlugin} from '@jupyterlab/application';
import {INotebookTracker} from '@jupyterlab/notebook';
import {IEditorLanguageRegistry} from '@jupyterlab/codemirror';
import {PostgreSQL, sql, SQLDialect} from '@codemirror/lang-sql';
import {LanguageSupport} from '@codemirror/language';
import {Decoration, DecorationSet, EditorView, ViewPlugin} from '@codemirror/view';
import {EditorState, RangeSetBuilder} from '@codemirror/state';

/**
 * Initialization data for the jupyter-ra-extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter-ra-extension:plugin',
  description: 'Relational Algebra Symbols in Jupyter Lab',
  autoStart: true,
  requires: [IEditorLanguageRegistry, INotebookTracker],
  activate: (app: JupyterFrontEnd, languages: IEditorLanguageRegistry, tracker: INotebookTracker) => {
    // send start message
    console.log('JupyterLab extension jupyter-ra-extension is activated!');

    // add toolbar commands
    const insertText = (text: string) => {
      const current = tracker.currentWidget;
      const notebook = current!.content;
      const activeCell = notebook.activeCell;

      activeCell!.editor!.replaceSelection!(text);
    };

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

    // add custom SQL+RA dialect to enable syntax highlighting
    const magic_commands = [
      'create', 'of', 'name',
      'load', 'name',
      'copy',
      'use',
      'load_tests',
      'test',
      'all', 'all_rows',
      'max_rows',
      'query_max_rows',
      'schema', 'only',
      'store',
      'sql',
      'ra', 'analyze',
      'all_ra',
      'dc',
      'all_dc',
      'auto_parser',
      'guess_parser',
      'plotly', 'title',
      'plotly_raw', 'title'
    ]

    const ra_operators = [
      'π',
      'σ',
      'β',
      'ρ',
      '×', 'x',
      '⋈',
      '⟕',
      '⟖',
      '⟗',
      '⋉',
      '⋊',
      '∪',
      '∩',
      '-',
      '÷',
    ]
    const ra_alternative_operators = [
      'pi',
      'sigma',
      'beta',
      'rho',
      'times',
      'join',
      'ljoin',
      'rjoin',
      'fjoin', 'ojoin',
      'lsjoin',
      'rsjoin',
      'cup',
      'cap'
    ]
    const ra_logic_operators = [
      '←', '∧', '∨', '¬', '=', '≠', '<', '≤', '≥', '>'
    ]

    const sqlraDialect = SQLDialect.define({
      ...PostgreSQL.spec,
      keywords: `${PostgreSQL.spec.keywords} ${magic_commands.join(' ')} ${ra_alternative_operators.join(' ')}`,
      operatorChars: `${PostgreSQL.spec.operatorChars}${ra_logic_operators.join('')}`
    });
    const sqlraLanguage = sql({dialect: sqlraDialect});

    const RADecorationPlugin = ViewPlugin.fromClass(
      class {
        decorations: DecorationSet;

        constructor(view: EditorView) {
          this.decorations = this.buildDecorations(view.state);
        }

        update(update: { state: EditorState, docChanged: boolean }) {
          if (!update.docChanged)
            return

          this.decorations = this.buildDecorations(update.state);
        }

        buildDecorations(state: EditorState) {
          const builder = new RangeSetBuilder<Decoration>();

          for (let pos = 0; pos < state.doc.length; pos++) {
            if (ra_operators.includes(state.doc.sliceString(pos, pos + 1))) {
              builder.add(pos, pos + 1, Decoration.mark({
                class: 'cm-keyword-ra',
              }));
            }
          }

          return builder.finish();
        }
      },
      {
        decorations: v => v.decorations
      }
    );

    const sqlraSupport = new LanguageSupport(sqlraLanguage.language, [RADecorationPlugin]);

    const existingSQL = languages.findByMIME('text/x-sql');
    if (existingSQL) {
      existingSQL.support = sqlraSupport;
    } else {
      languages.addLanguage({
        name: 'sql-with-bowtie',
        mime: 'text/x-sql',
        extensions: ['.sql'],
        support: sqlraSupport
      });
    }
  }
};

export default plugin;
