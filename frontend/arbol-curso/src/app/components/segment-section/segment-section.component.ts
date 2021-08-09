import { Model } from './../../services/api.service';
import {Component, OnInit, ViewChild} from '@angular/core';
import {BaseComponent} from '../base.component';
import {Validators, AbstractControl} from '@angular/forms';



@Component({
    selector: 'app-segment-section',
    templateUrl: './segment-section.component.html',
    styleUrls: ['./segment-section.component.scss'],
})
export class SegmentSectionComponent extends BaseComponent implements OnInit {

  public type = Model.SegmentSection;
  public parentFieldName = 'segment';
  public section_order = [];

  public ngOnInit(): void {
    this.formGroup = this.formBuilder.group({
      id: [''],
      order: ['', Validators.required],
      questions_to_ask: [0, Validators.required]
    });
  }

  protected openModal(): void {
    super.openModal();
    this.apiService.segment_section_order(this.parentId).subscribe(res => {
      this.section_order = res;
    });
  }

  public openOrderModal(): void {
    this.apiService.segment_section_order(this.parentId).subscribe(res => {
        this.section_order = res;
        this.section_order.forEach(ss => {
          ss['name'] = 'Cuestionario ' + ss.order;
        });
        this.orderComp.openModal();
    });
  }

  public onCloseModal(): void {
    super.onCloseModal();
    this.formGroup.reset({ questions_to_ask: 0 });
}

}
