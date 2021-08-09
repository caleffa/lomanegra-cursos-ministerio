import {Component, OnInit} from '@angular/core';
import {BaseComponent} from '../base.component';
import {Validators} from '@angular/forms';
import { Model } from './../../services/api.service';



@Component({
    selector: 'app-downloadable-document',
    templateUrl: './downloadable-document.component.html',
    styleUrls: ['./downloadable-document.component.scss'],
})
export class DownloadableDocumentComponent extends BaseComponent implements OnInit {

    public type = Model.DownloadableDocument;
    public imgFieldName = 'document';
    public parentFieldName = 'video';

    public ngOnInit(): void {
        this.formGroup = this.formBuilder.group({
          id: [''],
          name: [''],
          document: ['', Validators.required],
          is_mandatory: [true],
        });
    }

    public onCloseModal(): void {
        super.onCloseModal();
        this.formGroup.reset({ document: '', is_mandatory: true });
    }

}
