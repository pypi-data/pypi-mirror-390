import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';

const PLUGIN_ID = 'pyxel-config-lab:plugin';
const COMMAND_ID = 'pyxel-config-lab:open';

const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  activate: async (app: JupyterFrontEnd, palette: ICommandPalette | null) => {
    console.log('✅ Pyxel Config Lab extension activated');

    const { commands, shell } = app;

    // Register command
    commands.addCommand(COMMAND_ID, {
      label: 'Open Pyxel Config Lab',
      execute: () => {
        console.log('Opening Pyxel Config Lab panel...');
        const panel = new Widget();
        panel.id = 'pyxel-config-lab-panel';
        panel.title.label = 'Pyxel Config Lab';
        panel.title.closable = true;

        const iframe = document.createElement('iframe');
        iframe.src = 'https://pyxel-config-lab-ede25c.gitlab.io/';
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        panel.node.appendChild(iframe);

        shell.add(panel, 'main');
        shell.activateById(panel.id);
      }
    });

    if (palette) palette.addItem({ command: COMMAND_ID, category: 'Pyxel' });

    // ---- Communication bridge between Python and JupyterLab ----
    async function attachToCurrentKernel() {
      try {
        const running = Array.from(app.serviceManager.sessions.running());
        if (running.length === 0) {
          console.warn('⚠️ No active Jupyter kernel sessions found.');
          return;
        }

        for (const model of running) {
          const session = await app.serviceManager.sessions.connectTo({
            model
          });
          const kernel = session.kernel;
          if (!kernel) continue;

          // Register a comm target that Python can talk to
          kernel.registerCommTarget('pyxel-config-lab', (comm: any) => {
            console.log('🎯 Comm target registered: pyxel-config-lab');

            comm.onMsg = (msg: any) => {
              const data = msg?.content?.data;
              if (data?.event === 'open-pyxel-config-lab') {
                console.log('🚀 Received open command from Python');
                app.commands.execute(COMMAND_ID);
              }
            };
          });
        }
      } catch (err) {
        console.error('❌ Error attaching comm target:', err);
      }
    }

    // Run once immediately, and reattach whenever sessions change
    await attachToCurrentKernel();
    app.serviceManager.sessions.runningChanged.connect(attachToCurrentKernel);

    console.log('🔗 Ready to receive comm messages from Python...');
  }
};

export default plugin;
