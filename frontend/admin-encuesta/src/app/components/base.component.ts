import { Input, Injectable, OnInit, Output, EventEmitter } from '@angular/core';
import { Controller } from '../app.component';
import { APIService } from '../services/api.service';
import { Observable } from 'rxjs';
import { FormControl, FormBuilder, Validators, FormArray } from '@angular/forms';

@Injectable()
export class BaseComponent implements OnInit {    

    @Input() controller: Controller;
    @Output('reload') reload: EventEmitter<any> = new EventEmitter();

    public validationMessages: any;
    public optionsToDelete: any[] = new Array<any>();
    public noOpcion: boolean;

    constructor(public apiService: APIService,
        public fb: FormBuilder) {
    }

    public ngOnInit(): void {
        this.controller.isEditing.subscribe(val => {
            if (val) {
                this.controller.formGroup.enable();
            } else {
                this.controller.formGroup.disable();
            }
        });
        this.initValidationMessages();
        this.noOpcion = this.getOpciones().length == 0;
    }

    public trackByFn(index, item) {
        return index;  
    }

    protected initValidationMessages(): void {
        this.validationMessages = {
          'texto': [{ type: 'required', message: 'Ingrese un texto' }]
        };
    }

    public showErrors(controlName: string, validation: any): boolean {
        const control = this.controller.formGroup.get(controlName);
        return control.hasError(validation.type);
    }

    public getImageUrl(imagen: string): string {
        return this.controller.formGroup.value[imagen];
    }

    public getOpciones(): any[] {
        return this.controller.formGroup['controls'].opciones.value;
    }

    public addOption(): void {
        this.controller.formGroup['controls'].opciones['push'](this.fb.group({
            texto: ['', Validators.required]
        }));
        this.noOpcion = false;
    }

    public removeOpcion(opcion: any, index: number): void {
        if(this.controller.isEditing.value) {
            let formAr = this.controller.formGroup['controls'].opciones as FormArray;
            formAr.removeAt(index);
            this.optionsToDelete.push(opcion);
        }
        this.noOpcion = this.getOpciones().length == 0;
    }

    public uploadImage(event: any, imgFieldName: string): void {
        if (event.target.files && event.target.files[0]) {
            let reader = new FileReader();
            reader.onload = () => {
                this.controller.formGroup.get(imgFieldName).setValue(event.target.files[0]);
            };
            reader.readAsDataURL(event.target.files[0]);
        }
    }

    public save(): void {
        if(this.controller.formGroup.valid) {
            let observable: Observable<any>;
            let controls = this.controller.formGroup.controls;
            let data = new FormData();
            Object.keys(controls).forEach(key => {
                if(controls[key].value && key != 'opciones') {
                    data.append(key, controls[key].value);
                } else if (key == 'opciones') {
                    let json = JSON.stringify(controls[key].value)
                    data.append('opciones_json', json)
                }
            });
            if(controls['id'].value) {
                observable = this.apiService.update(controls['id'].value.toString(), data);
                this.deleteOpciones();
            } else {
                observable = this.apiService.create(data);
            }
            observable.subscribe(rta => {
                this.reset();
            });
        }
    }

    public deleteOpciones(): void {
        let opciones = this.optionsToDelete.filter(o=>o==o);
        opciones.forEach(op => { 
            this.apiService.deleteOpcion(op.id).subscribe(_=>{});
            this.optionsToDelete = this.optionsToDelete.fill(o=>o!=op);
        });
    }

    public reset(): void {
        this.reload.emit();
        this.optionsToDelete = new Array<any>();
    }

}