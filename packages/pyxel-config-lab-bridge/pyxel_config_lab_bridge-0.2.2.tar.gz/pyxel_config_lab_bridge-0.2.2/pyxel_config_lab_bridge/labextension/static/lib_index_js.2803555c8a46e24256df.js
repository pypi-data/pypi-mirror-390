"use strict";
(self["webpackChunkpyxel_config_lab"] = self["webpackChunkpyxel_config_lab"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);

const PLUGIN_ID = 'pyxel-config-lab:plugin';
const COMMAND_ID = 'pyxel-config-lab:open';
const plugin = {
    id: PLUGIN_ID,
    autoStart: true,
    activate: async (app, palette) => {
        console.log('✅ Pyxel Config Lab extension activated');
        const { commands, shell } = app;
        // Register command
        commands.addCommand(COMMAND_ID, {
            label: 'Open Pyxel Config Lab',
            execute: () => {
                console.log('Opening Pyxel Config Lab panel...');
                const panel = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget();
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
        if (palette)
            palette.addItem({ command: COMMAND_ID, category: 'Pyxel' });
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
                    if (!kernel)
                        continue;
                    // Register a comm target that Python can talk to
                    kernel.registerCommTarget('pyxel-config-lab', (comm) => {
                        console.log('🎯 Comm target registered: pyxel-config-lab');
                        comm.onMsg = (msg) => {
                            var _a;
                            const data = (_a = msg === null || msg === void 0 ? void 0 : msg.content) === null || _a === void 0 ? void 0 : _a.data;
                            if ((data === null || data === void 0 ? void 0 : data.event) === 'open-pyxel-config-lab') {
                                console.log('🚀 Received open command from Python');
                                app.commands.execute(COMMAND_ID);
                            }
                        };
                    });
                }
            }
            catch (err) {
                console.error('❌ Error attaching comm target:', err);
            }
        }
        // Run once immediately, and reattach whenever sessions change
        await attachToCurrentKernel();
        app.serviceManager.sessions.runningChanged.connect(attachToCurrentKernel);
        console.log('🔗 Ready to receive comm messages from Python...');
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.2803555c8a46e24256df.js.map