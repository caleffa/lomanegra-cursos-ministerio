import { Component, OnInit } from '@angular/core';
import { BaseComponent } from '../base.component';

@Component({
  selector: 'app-excluyente',
  templateUrl: './excluyente.component.html',
  styleUrls: ['./excluyente.component.scss']
})
export class ExcluyenteComponent extends BaseComponent implements OnInit{

  public ngOnInit(): void {
    super.ngOnInit();
    if(!this.controller.formGroup.value.id) {
      this.addOption();
    }
  }

}
