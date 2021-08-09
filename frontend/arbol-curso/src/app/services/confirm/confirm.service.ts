import { ConfirmComponent } from './confirm.component';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { Observable, of } from 'rxjs';
import { Injectable } from '@angular/core';



@Injectable()
export class ConfirmService {

  constructor(private _modalService: NgbModal) {}

  askForConfirmation(
    message = "",
    title = "Confirmación",
    confirmText = "Aceptar",
    cancelText = "Cancelar",
    showCloseButton = true,
  ): Observable<boolean> {
    const modalRef = this._modalService.open(ConfirmComponent);
    modalRef.componentInstance.message = message;
    modalRef.componentInstance.title = title;
    modalRef.componentInstance.confirmText = confirmText;
    modalRef.componentInstance.cancelText = cancelText;
    modalRef.componentInstance.showCloseButton = showCloseButton;
    // modalRef.componentInstance.messages = (message instanceof Array) ? message : [message];

    return new Observable(observer => {
      modalRef.result.catch(() => of(false).subscribe(observer)).then(() => of(true).subscribe(observer));
    });
  }
}
