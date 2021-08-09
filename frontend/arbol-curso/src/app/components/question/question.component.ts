import { Model } from './../../services/api.service';
import {Component, OnInit} from '@angular/core';
import {BaseComponent} from '../base.component';
import {Validators} from '@angular/forms';



@Component({
    selector: 'app-question',
    templateUrl: './question.component.html',
    styleUrls: ['./question.component.scss'],
})
export class QuestionComponent extends BaseComponent implements OnInit {

    public type = Model.Question;
    public parentFieldName = 'section';
    public imgFieldName = 'image';
    public segment_order = [];

    public ngOnInit(): void {
        this.formGroup = this.formBuilder.group({
          id: [''],
          text: ['', Validators.required],
          image: [''],
          has_only_one_correct_answer: [true, Validators.required],
          show_correct_options: [1, Validators.required],
          show_incorrect_options: ['', Validators.required],
          text_after_correct_answer: [''],
          text_after_incorrect_answer: ['']
        });
    }

    public onCloseModal(): void {
        super.onCloseModal();
        this.formGroup.reset({
            image: '',
            has_only_one_correct_answer: true,
            show_correct_options: 1,
            text_after_correct_answer: '',
            text_after_incorrect_answer: ''
        });
    }

}
