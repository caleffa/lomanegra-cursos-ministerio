import { Component, ViewChild, Input } from "@angular/core";
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
    selector: 'order-modal',
    templateUrl: 'order-modal.component.html'
})
export class OrderModalComponent {
    
    @Input() data: Array<{order:number, name:string}>;
    @Input() title: string;

    @ViewChild('orderModal', {static: false}) protected orderModal;
    
    constructor(private modalService: NgbModal) {
    }

    public openModal(): void {
        this.modalService.open(this.orderModal);
    }

}