import { Model } from './../../services/api.service';
import {Component, OnInit} from '@angular/core';
import {BaseComponent} from '../base.component';
import {Validators} from '@angular/forms';
import {HttpEvent, HttpEventType, HttpErrorResponse} from '@angular/common/http';
import { map } from 'rxjs/operators';
import { filterTrue } from 'src/app/helpers/observable-helpers';



@Component({
    selector: 'app-tarea',
    templateUrl: './tarea.component.html',
    styleUrls: ['./tarea.component.scss'],
})
export class TareaComponent extends BaseComponent implements OnInit {

    public archivo: any;
    public type = Model.Tarea;
    public parentFieldName = 'segmento';
    public viejosAdjuntos = new Array<any>();
    public nuevosArchivos = new Array<any>();
    public nuevosArchivosIds = new Array<number>();
    public barWidth: number = 0;
    public mensajeErrorArchivo: string;

    public ngOnInit(): void {
        this.formGroup = this.formBuilder.group({
          id: [''],
          titulo: ['', Validators.required],
          descripcion: ['', Validators.required],
          obligatoria: [false, Validators.required],
          archivo: []
        });
    }

    public load(id: number, parentId: number): void {
        this.parentId = parentId;
        this.apiService.get(this.type, id).subscribe(rta => {
            this.isEditing = true;
            this.viejosAdjuntos = rta['adjuntos_data'].filter(e=>e==e);
            this.formGroup.patchValue(rta);
            this.openModal();
        })
    }

    public getLink() {
        let prev = window.location.href;
        return `/tareas/${this.formGroup.get('id').value}?prev=${prev}`;
    }

    public setArchivo(event: any): void {
        if (event.target.files && event.target.files[0]) {
            const reader = new FileReader();
            reader.onload = () => {
                this.archivo = event.target.files[0];
            };
            reader.readAsDataURL(event.target.files[0]);
        }
    }

    public adjuntar(): void {
        this.nuevosArchivos.push(this.archivo);
        this.archivo = null;
        this.formGroup.get('archivo').setValue(null);
    }

    public borrarArchivo(archivo: any) {
        this.nuevosArchivos = this.nuevosArchivos.filter(a => a!=archivo);
    }

    public borrarAdjunto(adjunto: any) {
        this.viejosAdjuntos = this.viejosAdjuntos.filter(a => a!=adjunto);
    }

    public saveFiles(): void {
        if(this.formGroup.valid) {
            filterTrue(this.confirmService.askForConfirmation("¿Desea guardar los cambios?")).subscribe(() => this._saveFiles());
        } else {
            this.showErrors = true;
        }
    }

    private _saveFiles() {
        if(this.nuevosArchivos.length > 0) {
            let formData = new FormData();
            formData.append('archivo', this.nuevosArchivos[0]);
            this.apiService.createWithProgress('adjunto', formData).pipe(map(resp => {
                this.manageResponse(resp);
                return resp
            })).subscribe((evt: HttpEvent<any> | HttpErrorResponse) => {
                switch (evt.type) {
                    case HttpEventType.UploadProgress:
                        const porcentaje = Math.floor((evt.loaded / evt.total) * 100);
                        this.barWidth = porcentaje;
                        break;
                    case HttpEventType.Response:
                        this.nuevosArchivos = this.nuevosArchivos.filter(a => a!=this.nuevosArchivos[0]);
                        this.nuevosArchivosIds.push(evt['body'].id);
                        this._saveFiles();
                        break;
                }
            })
        } else {
            this.doSave();
        }
    }

    private manageResponse(resp: any) {
        if(!resp['ok'] && resp['ok'] != undefined) {
            if(resp['status']==413 && resp['status'] != undefined) {
                this.mensajeErrorArchivo = 'El archivo ' + this.nuevosArchivos[0].name + ' es demasiado grande.';
            } else {
                this.mensajeErrorArchivo = 'Ocurrió un error al subir el archivo ' + this.nuevosArchivos[0].name;
            }
        } else if(resp['ok'] != undefined){
            this.mensajeErrorArchivo = null;
        }
    }

    private doSave(): void {
        this.showErrors = false;
        let data = {};
        Object.keys(this.formGroup.controls).forEach(key => {
            const formControl = this.formGroup.controls[key];
            if (formControl.enabled && key != 'id' && key != 'archivo') {
                data[key] = formControl.value;
            }
        });
        let ids = this.nuevosArchivosIds.filter(a=>a==a);
        this.viejosAdjuntos.forEach(a => {
            ids.push(a.id);
        });
        data['adjuntos'] = ids;
        let observable;
        if(this.formGroup.controls['id'].value) {
            observable = this.apiService.update(this.type, this.formGroup.controls['id'].value, data);
        } else {
            data[this.parentFieldName] = this.parentId.toString();
            observable = this.apiService.create(this.type, data);
        }
        observable.subscribe(rta => {
            this.refresh.emit();
            this.onCloseModal();
        });
    }

    protected onCloseModal(): void {
        this.viejosAdjuntos = new Array<any>();
        this.nuevosArchivos = new Array<any>();
        this.nuevosArchivosIds = new Array<number>();
        this.barWidth = 0;
        super.onCloseModal();
        this.formGroup.get('obligatoria').setValue(false);
        this.archivo = null;
        this.mensajeErrorArchivo = null;
    }

}
