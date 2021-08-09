import {Component, OnInit, ViewChild} from '@angular/core';
import {BaseComponent} from '../base.component';
import {Validators} from '@angular/forms';
import { Model } from './../../services/api.service';



@Component({
    selector: 'app-forum',
    templateUrl: './forum.component.html',
    styleUrls: ['./forum.component.scss'],
})
export class ForumComponent extends BaseComponent implements OnInit {

    public type = Model.Forum;
    public parentFieldName = 'segment';
    public forum_order = [];

    public ngOnInit(): void {
        this.formGroup = this.formBuilder.group({
          id: [''],
          title: ['', Validators.required],
          order: ['', Validators.required]
        });
    }

    public openOrderModal(): void {
        this.apiService.forum_order(this.parentId).subscribe(res => {
            this.forum_order = res;
            this.orderComp.openModal();
        });
    }

}
