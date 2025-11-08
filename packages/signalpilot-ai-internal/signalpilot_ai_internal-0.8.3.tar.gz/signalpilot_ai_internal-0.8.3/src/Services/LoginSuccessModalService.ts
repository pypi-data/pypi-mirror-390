import * as React from 'react';
import { Widget } from '@lumino/widgets';
import { ReactWidget } from '@jupyterlab/ui-components';
import {
  LoginSuccessModal,
  LoginSuccessModalProps
} from '../Components/LoginSuccessModal';
import { AppStateService } from '../AppState';

/**
 * React Widget wrapper for the LoginSuccessModal
 */
class LoginSuccessModalWidget extends ReactWidget {
  private modalService: LoginSuccessModalService;

  constructor(modalService: LoginSuccessModalService) {
    super();
    this.modalService = modalService;
    this.addClass('sage-ai-login-success-modal-widget');
    this.id = 'sage-ai-login-success-modal';
  }

  render(): React.ReactElement {
    console.log(
      '[LoginSuccessModalWidget] Rendering with props:',
      this.modalService.getModalProps()
    );
    return React.createElement(
      LoginSuccessModal,
      this.modalService.getModalProps()
    );
  }
}

/**
 * Service for managing the login success modal
 */
export class LoginSuccessModalService {
  private static instance: LoginSuccessModalService | null = null;
  private widget: LoginSuccessModalWidget | null = null;
  private isShowing = false;

  private constructor() {}

  /**
   * Get the singleton instance
   */
  public static getInstance(): LoginSuccessModalService {
    if (!LoginSuccessModalService.instance) {
      LoginSuccessModalService.instance = new LoginSuccessModalService();
    }
    return LoginSuccessModalService.instance;
  }

  /**
   * Show the login success modal
   */
  public show(): void {
    console.log('[LoginSuccessModalService] show() called, current state:', {
      isShowing: this.isShowing,
      widgetExists: !!this.widget
    });

    if (this.isShowing) {
      console.log(
        '[LoginSuccessModalService] Already showing, returning early'
      );
      return;
    }

    this.isShowing = true;

    if (!this.widget) {
      console.log('[LoginSuccessModalService] Creating new ReactWidget');
      this.widget = new LoginSuccessModalWidget(this);
    }

    // Add to document body
    console.log(
      '[LoginSuccessModalService] Adding ReactWidget to document body'
    );
    Widget.attach(this.widget, document.body);

    console.log(
      '[LoginSuccessModalService] Login success modal ReactWidget attached successfully'
    );
  }

  /**
   * Hide the login success modal
   */
  public hide(): void {
    console.log('[LoginSuccessModalService] hide() called');

    if (!this.isShowing) {
      console.log('[LoginSuccessModalService] Not showing, returning early');
      return;
    }

    this.isShowing = false;

    if (this.widget) {
      console.log('[LoginSuccessModalService] Detaching and disposing widget');
      Widget.detach(this.widget);
      this.widget.dispose();
      this.widget = null;
    }

    console.log('[LoginSuccessModalService] Login success modal hidden');
  }

  /**
   * Handle user clicking close or auto-close
   */
  private handleClose(): void {
    console.log(
      '[LoginSuccessModalService] User closed modal or auto-close triggered'
    );
    this.hide();
  }

  /**
   * Get the modal props
   */
  public getModalProps(): LoginSuccessModalProps {
    return {
      isVisible: this.isShowing,
      onClose: () => this.handleClose()
    };
  }

  /**
   * Update the widget to reflect current state
   */
  public update(): void {
    if (this.widget) {
      this.widget.update();
    }
  }

  /**
   * Get debug information
   */
  public getDebugInfo() {
    return {
      isShowing: this.isShowing,
      hasWidget: !!this.widget,
      widgetAttached: this.widget ? this.widget.isAttached : false,
      widgetDisposed: this.widget ? this.widget.isDisposed : false
    };
  }

  /**
   * Show login success modal after successful authentication
   * This is the main public method to trigger the success modal
   * Will skip showing if on launcher and tour not completed
   */
  public static async showLoginSuccess(): Promise<void> {
    console.log('[LoginSuccessModalService] showLoginSuccess() called');

    try {
      const { AppStateService } = await import('../AppState');

      const isLauncherActive = AppStateService.isLauncherActive();
      const tourCompleted = await AppStateService.hasCompletedWelcomeTour();

      console.log('[LoginSuccessModalService] State check:', {
        isLauncherActive,
        tourCompleted
      });

      // Only show the login success modal if:
      // 1. Not on launcher, OR
      // 2. Tour is already completed
      const shouldShowModal = tourCompleted;

      if (!shouldShowModal) {
        console.log(
          '[LoginSuccessModalService] ❌ Skipping modal - on launcher and tour not completed'
        );
        return;
      }

      console.log('[LoginSuccessModalService] ✅ Showing modal');
      const instance = LoginSuccessModalService.getInstance();
      instance.show();
    } catch (error) {
      console.error(
        '[LoginSuccessModalService] Error checking if should show modal:',
        error
      );
      // Show anyway if check fails
      const instance = LoginSuccessModalService.getInstance();
      instance.show();
    }
  }

  /**
   * Debug method to test the modal - can be called from console
   */
  public static debugShow(): void {
    console.log(
      '[LoginSuccessModalService] Debug: Showing login success modal'
    );
    LoginSuccessModalService.showLoginSuccess();
  }
}
