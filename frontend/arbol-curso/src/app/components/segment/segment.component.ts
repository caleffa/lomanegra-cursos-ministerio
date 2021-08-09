import { Model } from './../../services/api.service';
import {Component, OnInit, Input} from '@angular/core';
import {BaseComponent} from '../base.component';
import {Validators} from '@angular/forms';
import * as moment from 'moment';
import { filter } from 'rxjs/operators';
import { filterTrue } from 'src/app/helpers/observable-helpers';



@Component({
    selector: 'app-segment',
    templateUrl: './segment.component.html',
    styleUrls: ['./segment.component.scss'],
})
export class SegmentComponent extends BaseComponent implements OnInit {

    public type = Model.Segment;
    public parentFieldName = 'course';
    public imgFieldName = 'thumbnail';
    public segment_order = [];
    protected dateTimeFields = ['enabled_since'];
    private slides: any[] = new Array<any>();

    public ngOnInit(): void {
        this.formGroup = this.formBuilder.group({
            id: [''],
            title: ['', Validators.required],
            type_of_segment: ['V', Validators.required],
            max_retries: [0, Validators.required],
            min_correct_questions: [0, Validators.required],
            order: ['', Validators.required],
            enabled_since_date: [null],
            enabled_since_time: [null],
            vimeo_id: [0, Validators.required],
            genially_id: [0, Validators.required],
            embed_code: [null, Validators.required],
            requires_full_watch: [true, Validators.required]
        });

        this.formGroup.controls['type_of_segment'].valueChanges.subscribe( type_of_segment => {
            if (type_of_segment == 'V') {
                this.formGroup.controls['vimeo_id'].enable();
            } else {
                this.formGroup.controls['vimeo_id'].disable();
            }
            if (type_of_segment == 'G') {
                this.formGroup.controls['genially_id'].enable();
            } else {
                this.formGroup.controls['genially_id'].disable();
            }
            if (type_of_segment == 'X') {
                this.formGroup.controls['embed_code'].enable();
            } else {
                this.formGroup.controls['embed_code'].disable();
            }
        });
        this.showErrors = false;
    }

    public openOrderModal(): void {
        this.apiService.segment_order(this.parentId).subscribe(res => {
            this.segment_order = res;
            this.orderComp.openModal();
        });
    }

    public onCloseModal(): void {
        super.onCloseModal();
        this.formGroup.reset({
            type_of_segment: 'V',
            max_retries: 0,
            min_correct_questions: 0
        });
    }

    public selectSlides(event: any): void {
        this.slides = event.target.files;
    }

    public formIsValid(): boolean {
        return this.formGroup.valid
            && ((this.formGroup.controls['type_of_segment'].value == 'S' && this.slides.length > 0)
            || this.formGroup.controls['type_of_segment'].value == 'V'
            || this.formGroup.controls['type_of_segment'].value == 'G'
            || this.formGroup.controls['type_of_segment'].value == 'X'
            || this.isEditing);
    }

    public save(): void {
        if(this.formIsValid()) {
            filterTrue(this.confirmService.askForConfirmation("¿Desea guardar los cambios?")).subscribe(() => {
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
                    if(this.formGroup.controls['type_of_segment'].value == 'S' && !this.isEditing) {
                        console.log(rta);
                        this.createSlides(rta.id);
                    } else {
                        this.reset();
                    }
                });
            });
        } else {
            this.showErrors = true;
        }
    }

    private createSlides(id: number) {
        if(this.slides.length > 0) {
            let obs = this.saveSlide(id, this.slides[0]);
            obs.subscribe(rta => {
                let newSlides = new Array<any>();
                for(let i=0; i<this.slides.length; i++) {
                    if(i!=0) {
                        newSlides.push(this.slides[i]);
                    }
                }
                this.slides = newSlides;
                this.createSlides(id);
            });
        } else {
            this.reset();
        }
    }

    private saveSlide(id: number, image: any) {
        let data = new FormData();
        data.append('segment', id.toString());
        data.append('image', image);
        return this.apiService.create('slide', data);
    }

    private reset(): void {
        this.imgLink = null;
        this.refresh.emit();
        this.onCloseModal();
    }

}
