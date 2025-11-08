"use strict";

sap.ui.define(["./BaseController", "sap/ui/Device", "sap/m/MessageBox"], function (__BaseController, Device, MessageBox) {
  "use strict";

  function _interopRequireDefault(obj) {
    return obj && obj.__esModule && typeof obj.default !== "undefined" ? obj.default : obj;
  }
  const BaseController = _interopRequireDefault(__BaseController);
  /**
   * @namespace com.optrabot.ui.controller
   */
  const App = BaseController.extend("com.optrabot.ui.controller.App", {
    onInit: function _onInit() {
      // apply content density mode to root view
      this.getView().addStyleClass(this.getOwnerComponent().getContentDensityClass());

      // if the app starts on desktop devices with small or medium screen size, collaps the side navigation
      if (Device.resize.width <= 1024) {
        this.onSideNavButtonPress();
      }
    },
    getBundleText: function _getBundleText(sI18nKey, aPlaceholderValues) {
      return Promise.resolve(this.getBundleTextByModel(sI18nKey, this.getOwnerComponent().getModel("i18n"), aPlaceholderValues));
    },
    onShutdownPress: async function _onShutdownPress() {
      console.log("Shutdown button pressed");
      const globalModel = this.getOwnerComponent().getModel("global");
      const backendBaseUrl = globalModel.getProperty("/backendBaseUrl");
      try {
        const response = await fetch(`${backendBaseUrl}/api/shutdown`, {
          method: 'POST'
        });
        if (response.ok) {
          const result = await response.json();
          console.log("Shutdown request successful", result);
          await this.showShutdownConfirmationPage();
        } else {
          console.error("Shutdown request failed with status:", response.status);
          MessageBox.error("Fehler beim Herunterfahren des OptraBots.", {
            title: "Shutdown Fehler"
          });
        }
      } catch (error) {
        console.error("Error occurred while shutting down:", error);
        MessageBox.error("Ein unerwarteter Fehler ist beim Herunterfahren aufgetreten.", {
          title: "Unerwarteter Fehler"
        });
      }
    },
    showShutdownConfirmationPage: async function _showShutdownConfirmationPage() {
      // Hole die lokalisierten Texte
      const title = await this.getBundleText("shutdownPageTitle");
      const description = await this.getBundleText("shutdownPageDescription");
      const instruction = await this.getBundleText("shutdownPageInstruction");
      const buttonText = await this.getBundleText("shutdownPageButtonText");
      const buttonTooltip = await this.getBundleText("shutdownPageButtonTooltip");

      // Ändere den Seitentitel sofort
      document.title = `OptraBot - ${title}`;

      // Erstelle eine saubere Shutdown-Seite mit DOM-Manipulation
      // Dies verhindert Konflikte mit der bestehenden NavigationList
      setTimeout(() => {
        document.body.innerHTML = `
				<!DOCTYPE html>
				<html>
				<head>
					<meta charset="utf-8">
					<meta name="viewport" content="width=device-width, initial-scale=1.0">
					<title>OptraBot - ${title}</title>
					<link rel="icon" type="image/png" href="img/favicon.png">
					<link rel="stylesheet" href="https://sdk.openui5.org/1.132.1/resources/sap/ui/core/themes/sap_horizon/library.css">
					<style>
						body, html {
							margin: 0;
							padding: 0;
							height: 100vh;
							font-family: '72', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
							background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
							display: flex;
							align-items: center;
							justify-content: center;
						}
						
						.shutdown-container {
							background: rgba(255, 255, 255, 0.98);
							border-radius: 12px;
							padding: 48px 40px;
							text-align: center;
							box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
							max-width: 520px;
							width: 90%;
							border: 1px solid rgba(0, 0, 0, 0.1);
						}
						
						.success-icon {
							width: 50px;
							height: 50px;
							margin: 0 auto 32px;
							background: #4CAF50;
							border-radius: 50%;
							display: flex;
							align-items: center;
							justify-content: center;
							color: white;
							font-size: 40px;
							font-weight: 300;
						}
						
						.shutdown-title {
							font-size: 28px;
							font-weight: 400;
							color: #333;
							margin-bottom: 24px;
							line-height: 1.2;
						}
						
						.shutdown-description {
							font-size: 16px;
							color: #666;
							margin-bottom: 20px;
							line-height: 1.6;
						}
						
						.shutdown-instruction {
							font-size: 16px;
							color: #333;
							margin-bottom: 32px;
							font-weight: 600;
						}
						
						.close-button {
							background: #0854a0;
							color: white;
							border: none;
							padding: 12px 24px;
							border-radius: 6px;
							font-size: 14px;
							font-weight: 500;
							cursor: pointer;
							transition: all 0.2s ease;
							min-width: 200px;
						}
						
						.close-button:hover {
							background: #0a5d9e;
							box-shadow: 0 2px 8px rgba(8, 84, 160, 0.3);
						}
						
						.close-button:active {
							transform: translateY(1px);
						}
						
						.close-button:focus {
							outline: 2px solid #0854a0;
							outline-offset: 2px;
						}
					</style>
				</head>
				<body>
					<div class="shutdown-container">
						<div class="success-icon">✓</div>
						<h1 class="shutdown-title">${title}</h1>
						<p class="shutdown-description">
							${description.replace(/\\n/g, '<br>')}
						</p>
						<p class="shutdown-instruction">
							${instruction}
						</p>
						<button class="close-button" onclick="window.close();" title="${buttonTooltip}">
							${buttonText}
						</button>
					</div>
					
					<script>
						// Fokus auf den Button setzen für Keyboard-Navigation
						document.querySelector('.close-button').focus();
						
						// Tastaturunterstützung
						document.addEventListener('keydown', function(e) {
							if (e.key === 'Escape' || (e.ctrlKey && e.key === 'w') || (e.metaKey && e.key === 'w')) {
								window.close();
							}
						});
					</script>
				</body>
				</html>
			`;
      }, 500); // Kurze Verzögerung um sicherzustellen, dass der API-Call abgeschlossen ist
    },
    onSideNavButtonPress: function _onSideNavButtonPress() {
      console.log("SideNavButton pressed");
      const oToolPage = this.byId("optrabot_app");
      var bSideExpanded = oToolPage.getSideExpanded();
      oToolPage.setSideExpanded(!bSideExpanded);
      this._setToggleButtonTooltip(!bSideExpanded);
    },
    _setToggleButtonTooltip: async function _setToggleButtonTooltip(bSideExpanded) {
      const oToggleButton = this.byId("sideNavigationToggleButton");
      if (bSideExpanded) {
        oToggleButton.setTooltip(await this.getBundleText("sideNavigationCollapseTooltip"));
      } else {
        oToggleButton.setTooltip(await this.getBundleText("sideNavigationExpandTooltip"));
      }
    }
  });
  return App;
});
//# sourceMappingURL=App-dbg.controller.js.map
