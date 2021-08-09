import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ConfirmService } from './../../services/confirm/confirm.service';
import { Model, CoursesAPIService } from './../../services/api.service';
import { Component, OnInit } from '@angular/core';
import { BaseComponent } from '../base.component';
import { Validators, FormArray, FormGroup, FormBuilder } from '@angular/forms';
import { flattenValues, mergeDatetimes, unmergeDatetimes, FormArrayHelpers } from 'src/app/helpers/form-helpers';
import { map } from 'rxjs/operators';
import * as _ from 'lodash';
import moment from "moment";
import { filterTrue } from 'src/app/helpers/observable-helpers';



enum AnnouncementTypes {
    Open = 'O',
    FixedDate = 'F',
}

function minDateTimeValidator(minDate: Date, dateName: string, timeName: string) {
    var validatorFunction = function (g: FormGroup) {
        const m = moment(`${g.get(dateName).value}T${g.get(timeName).value}:00-03:00`).zone('-03:00');
        return m >= moment(minDate)
      ? null : {'minDate': true};
    };
    return validatorFunction;
}

@Component({
    selector: 'app-live-stream',
    templateUrl: './live-stream.component.html',
    styleUrls: ['./live-stream.component.scss'],
})
export class LiveStreamComponent extends BaseComponent implements OnInit {
    public type = Model.LiveStream;
    public parentFieldName = 'course';
    public imgFieldName = 'thumbnail';
    public segment_order = [];
    protected dateTimeFields = ['enabled_since'];

    today = new Date();

    // forward al template
    AnnouncementTypes = AnnouncementTypes;

    public ngOnInit(): void {
        this.formGroup = this.formBuilder.group({
            id: [''],
            title: ['', Validators.required],
            order: ['', Validators.required],
            enabled_since_date: [null],
            enabled_since_time: [null],
            vimeo_id: [0, Validators.required],
            stream_key: [0, Validators.required],
            rtmp_url: [0, Validators.required],
            announcement_type: [AnnouncementTypes.FixedDate],
            fixed_dates_broadcast: this.formBuilder.group({
                dates: this.formBuilder.array([]),
            }),
            open_broadcast: this.formBuilder.group({
                open_broadcast_date_date: null,
                open_broadcast_date_time: null,
            }, {
                validators: minDateTimeValidator(this.today, 'open_broadcast_date_date', 'open_broadcast_date_time')
            }),
        });

        this.formGroup.get('announcement_type').valueChanges.subscribe(_ => this.switchAnnouncementTypeForms());
        this.switchAnnouncementTypeForms();

        this.showErrors = false;
    }

    addFixedDateForm() {
        const fixedDatesForms = this.formGroup.get('fixed_dates_broadcast.dates') as FormArray;
        fixedDatesForms.push(
            this.formBuilder.group({
                date_date: [null, Validators.required],
                date_time: [null, Validators.required],
            }, {
                validators: minDateTimeValidator(this.today, 'date_date', 'date_time')
            })
        );
    }

    deleteFixedDateFormAt(index: number) {
        const fixedDatesForms = this.formGroup.get('fixed_dates_broadcast.dates') as FormArray;
        fixedDatesForms.removeAt(index);
    }

    startStreaming() {
        filterTrue(this.confirmService.askForConfirmation("Desea comenzar a transmitir en vivo?")).subscribe(() => {
            this.apiService.start_streaming(this.formGroup.controls['id'].value).subscribe(res => {
                this.loadData(unmergeDatetimes(res));
            });
        });
    }

    stopStreaming() {
        filterTrue(this.confirmService.askForConfirmation("Desea detener la transmisión actual?")).subscribe(() => {
            this.apiService.stop_streaming(this.formGroup.controls['id'].value).subscribe(res => {
                this.loadData(unmergeDatetimes(res));
            });
        });
    }

    private switchAnnouncementTypeForms() {
        const announcementType = this.formGroup.get('announcement_type').value;
        if (announcementType === AnnouncementTypes.Open) {
            this.formGroup.get('open_broadcast').enable();
            this.formGroup.get('fixed_dates_broadcast').disable();
        }
        else if (announcementType === AnnouncementTypes.FixedDate) {
            this.formGroup.get('fixed_dates_broadcast').enable();
            this.formGroup.get('open_broadcast').disable();

            // si no hay ninguna fecha, agrego una (mínimo requerido)
            const datesForms = this.formGroup.get('fixed_dates_broadcast.dates') as FormArray;
            if (datesForms.length == 0) {
                this.addFixedDateForm();
            }
        }
    }

    public openOrderModal(): void {
        this.apiService.live_streams_order(this.parentId).subscribe(res => {
            this.segment_order = res;
            this.orderComp.openModal();
        });
    }

    protected openModal(): void {
        super.openModal();
        this.showErrors = false;
        this.resetForms();
    }

    protected resetForms() {
        const fixedDatesForms = this.formGroup.get('fixed_dates_broadcast.dates') as FormArray;
        FormArrayHelpers.clearFormArray(fixedDatesForms);
        const announcementTypeForm = this.formGroup.get('announcement_type');
        announcementTypeForm.enable();
        this.switchAnnouncementTypeForms();
        if (this.isEditing) {
            announcementTypeForm.disable();
        }
        else {
            announcementTypeForm.enable();
            announcementTypeForm.setValue(AnnouncementTypes.FixedDate);
        }
    }

    public onCloseModal(): void {
        super.onCloseModal();
        this.formGroup.reset({
            max_retries: 0,
            min_correct_questions: 0,
        });
    }

    public formIsValid(): boolean {
        return this.formGroup.valid;
    }

    public load(id: number, parentId: number): void {
        this.parentId = parentId;
        this.apiService.get(this.type, id).pipe(map(rta => {
            this.isEditing = true;
            const newRta = unmergeDatetimes(rta);
            return newRta
        })).subscribe(rta => {
            // están al revés que en BaseComponent porque el orden es importante en este componente
            this.openModal();
            this.loadData(rta);
        });
    }

    protected loadData(rta: {[key: string]: any}) {
        // crear la cantidad necesaria de forms en el formArray
        // TODO: verificar si hace falta o `patchValue` hace eso
        const fixedDatesForms = this.formGroup.get('fixed_dates_broadcast.dates') as FormArray;
        FormArrayHelpers.clearFormArray(fixedDatesForms);
        if (rta['fixed_dates_broadcast'] && rta['fixed_dates_broadcast']['dates']) {
            const dateCount = rta['fixed_dates_broadcast']['dates'].length;
            _.times(dateCount, () => this.addFixedDateForm());
        }

        super.loadData(rta);
    }

    public save(): void {
        if(this.formIsValid()) {
            filterTrue(this.confirmService.askForConfirmation("¿Desea guardar los cambios?")).subscribe(() => {
                this.showErrors = false;
                let data = new FormData();
                // se agrega por separado el announcement_type porque el form está deshabilitado en la edición
                const values = _.assign(this.formGroup.value, {announcement_type: this.formGroup.getRawValue()['announcement_type']});
                const cleanValues = mergeDatetimes(flattenValues(values));
                _.forEach(cleanValues, (value, key: string) => data.append(key, value));
                data.delete('id');

                let observable;
                if(this.formGroup.controls['id'].value) {
                    observable = this.apiService.update(this.type, this.formGroup.controls['id'].value, data);
                } else {
                    data.append(this.parentFieldName, this.parentId.toString());
                    observable = this.apiService.create(this.type, data);
                }
                observable.subscribe(rta => {
                    this.reset();
                });
            });
        } else {
            this.showErrors = true;
        }
    }

    private reset(): void {
        this.imgLink = null;
        this.refresh.emit();
        this.onCloseModal();
    }
}
