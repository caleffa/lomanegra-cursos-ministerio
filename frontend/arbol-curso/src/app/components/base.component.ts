import { ViewChild, Injectable, Output, EventEmitter, Input } from '@angular/core';
import { CoursesAPIService } from '../services/api.service';
import { ConfirmService } from './../services/confirm/confirm.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FormGroup, FormBuilder, AbstractControl } from '@angular/forms';
import { OrderModalComponent } from './order-modal/order-modal.component';
import { Model } from './../services/api.service';
import {map} from "rxjs/operators";
import * as moment from 'moment';
import * as _ from 'lodash';
import { filterTrue } from '../helpers/observable-helpers';



@Injectable()
export class BaseComponent {

    @Output() refresh: EventEmitter<any> = new EventEmitter();
    @Input() spinner: any;
    @ViewChild('componentModal', {static: false}) public modal;
    @ViewChild('orderComp', {static: false}) protected orderComp: OrderModalComponent;


    protected type: Model;
    protected parentFieldName: string;
    protected imgFieldName: string;
    public formGroup: FormGroup;
    protected parentId: number;
    protected imgLink: string;
    public data: any;
    protected dateTimeFields: Array<string> = [];
    public isEditing = false;

    public orderData: Array<{order:number, name:string}>;
    public showErrors: boolean = false;


    public errorMessages = {
        "required": "Este campo es obligatorio",
        "minDate": "La fecha no puede ser anterior",
    }

    constructor(
        protected apiService: CoursesAPIService,
        protected modalService: NgbModal,
        protected formBuilder: FormBuilder,
        protected confirmService: ConfirmService,
    ) {}

    public add(parentId: number): void {
        this.parentId = parentId;
        this.openModal();
    }

    public load(id: number, parentId: number): void {
        this.parentId = parentId;
        this.apiService.get(this.type, id).pipe(map(rta => {
            this.isEditing = true;
            let newRta = {...rta};
            for (const key of this.dateTimeFields) {
                if (key in newRta) {
                    let m = moment(newRta[key]);
                    m = m.zone('-03:00');
                    const d = m.format();
                    newRta[`${key}_date`] = !!newRta[key] ? d.slice(0, 10) : null;
                    newRta[`${key}_time`] = !!newRta[key] ? d.slice(11, 16) : null;
                    delete newRta[key];
                }
            }
            return newRta
        })).subscribe(rta => {
            this.loadData(rta);
            this.openModal();
        })
    }

    protected loadData(rta: {[key: string]: any}) {
        this.data = rta;
        this.formGroup.patchValue(rta);
        if(this.imgFieldName && rta[this.imgFieldName + '_url']) {
            this.imgLink = rta[this.imgFieldName + '_url'];
        }
    }

    public save(): void {
        if(this.formGroup.valid) {
            filterTrue(this.confirmService.askForConfirmation("Desea guardar los cambios?")).subscribe(() => {
                this.modalService.open(this.spinner, { backdrop: 'static', keyboard: false });
                this.showErrors = false;
                let data = new FormData();
                Object.keys(this.formGroup.controls).forEach(key => {
                    const formControl = this.formGroup.controls[key];
                    if (formControl.enabled) {
                        if (
                            (key.endsWith('_date') && this.dateTimeFields.indexOf(key.replace('_date', '')) !== -1) ||
                            (key.endsWith('_time') && this.dateTimeFields.indexOf(key.replace('_time', '')) !== -1) ||
                            (this.dateTimeFields.indexOf(key) !== -1)
                        ) {
                            // Skip
                        } else {
                            data.append(key, formControl.value);
                        }
                    }
                });
                for(const key of this.dateTimeFields) {
                    const dateFormControl = this.formGroup.controls[`${key}_date`];
                    const timeFormControl = this.formGroup.controls[`${key}_time`];
                    if (dateFormControl.enabled && timeFormControl.enabled) {
                        const m = moment(`${dateFormControl.value}T${timeFormControl.value}:00-03:00`).zone('-03:00')
                        if (m.isValid()) {
                            data.append(key, m.format());
                        }
                    }
                }
                data.delete('id');

                let observable;
                if(this.formGroup.controls['id'].value) {
                    observable = this.apiService.update(this.type, this.formGroup.controls['id'].value, data);
                } else {
                    data.append(this.parentFieldName, this.parentId.toString());
                    observable = this.apiService.create(this.type, data);
                }
                observable.subscribe(rta => {
                    this.imgLink = null;
                    this.refresh.emit();
                    this.onCloseModal();
                });
            });
        } else {
            this.showErrors = true;
        }
    }

    protected openModal(): void {
        this.modalService.open(this.modal, { size: 'lg'});
    }

    protected onCloseModal(): void {
        this.modalService.dismissAll()
        this.formGroup.reset();
        this.imgLink = null;
        this.isEditing = false;
    }

    public getValidity(ctrlPath: Array<string | number> | string): boolean {
        let control: AbstractControl = this.formGroup.get(ctrlPath);
        return control.errors && (control.touched || this.showErrors);
    }

    public getErrors(ctrlPath: Array<string | number> | string): string {
        let control: AbstractControl = this.formGroup.get(ctrlPath);
        if (control.errors) {
            return _.join(_.map(_.keys(control.errors), (e: string) => this.errorMessages[e] || "Campo inválido"), '\n');
        }
        return "";
    }

    public uploadDocument(event: any): void {
      if (event.target.files && event.target.files[0]) {
        const reader = new FileReader();
        reader.onload = () => {
            const formControl = this.formGroup.get(this.imgFieldName);
            if (!formControl) {
                this.formGroup.addControl(this.imgFieldName, this.formBuilder.control(''));
            }
            this.formGroup.controls[this.imgFieldName].setValue(event.target.files[0]);
        };
        reader.readAsDataURL(event.target.files[0]);
      }
    }

    public delete(id: number): void {
        this.modalService.open(this.spinner, { backdrop: 'static', keyboard: false });
        this.apiService.delete(this.type, id).subscribe(rta => {
            this.refresh.emit();
            this.modalService.dismissAll();
        });
    }

    public openOrderModal(): void {
        this.orderComp.openModal();
    }

}