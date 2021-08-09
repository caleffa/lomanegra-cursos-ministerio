import { Component, OnInit } from '@angular/core';
import { BaseComponent } from '../base.component';

@Component({
  selector: 'app-aditiva',
  templateUrl: './aditiva.component.html',
  styleUrls: ['./aditiva.component.scss']
})
export class AditivaComponent extends BaseComponent implements OnInit{

  public ngOnInit(): void {
    super.ngOnInit();
    if(!this.controller.formGroup.value.id) {
      this.addOption();
    }
    this.controller.formGroup.controls['aditiva_debe_contestar_al_menos_una'].setValue(true)
  }

}
