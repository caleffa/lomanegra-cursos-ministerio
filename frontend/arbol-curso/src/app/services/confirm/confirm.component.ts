import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';



@Component({
  selector: 'confirm',
  template: `
    <div class="modal-header">
      <h4 class="modal-title">{{ title }}</h4>
      <button type="button" class="close" aria-label="Close" (click)="activeModal.dismiss()">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
    <div class="modal-body">
      <p>{{ message }}</p>
    </div>
    <div class="modal-footer d-flex justify-content-around">
      <button type="button" class="btn btn-success" (click)="activeModal.close(true)">{{ confirmText }}</button>
      <button type="button" class="btn btn-danger" (click)="activeModal.dismiss()">{{ cancelText }}</button>
    </div>
  `
})
export class ConfirmComponent {
  @Input() title: string;
  @Input() confirmText: string;
  @Input() cancelText: string;
  @Input() showCloseButton: boolean;
  @Input() message: string;

  constructor(public activeModal: NgbActiveModal) {}
}
