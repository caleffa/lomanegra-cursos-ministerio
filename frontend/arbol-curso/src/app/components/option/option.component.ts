import { Model } from './../../services/api.service';
import {Component, OnInit, ViewChild} from '@angular/core';
import {BaseComponent} from '../base.component';
import {Validators} from '@angular/forms';



@Component({
    selector: 'app-option',
    templateUrl: './option.component.html',
    styleUrls: ['./option.component.scss'],
})
export class OptionComponent extends BaseComponent implements OnInit {

    public type = Model.Option;
    public parentFieldName = 'question';

    public ngOnInit(): void {
        this.formGroup = this.formBuilder.group({
          id: [''],
          text: ['', Validators.required],
          is_correct: [false, Validators.required]
        });
    }

    public onCloseModal(): void {
        super.onCloseModal();
        this.formGroup.reset({ is_correct: false });
    }
}
