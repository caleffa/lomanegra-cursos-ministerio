import { Model } from './../../services/api.service';
import {Component, OnInit} from '@angular/core';
import {BaseComponent} from '../base.component';
import {Validators} from '@angular/forms';



@Component({
    selector: 'app-slide',
    templateUrl: './slide.component.html',
    styleUrls: ['./slide.component.scss'],
})
export class SlideComponent extends BaseComponent implements OnInit {

    public type = Model.Slide;
    public parentFieldName = 'segment';
    public imgFieldName = 'image';

    public ngOnInit(): void {
        this.formGroup = this.formBuilder.group({
          id: [''],
          image: ['', Validators.required]
        });
    }

    public onCloseModal(): void {
        super.onCloseModal();
        this.formGroup.reset({ image: '' });
    }
}
