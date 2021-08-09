import { ConfirmService } from './confirm.service';
import { ConfirmComponent } from './confirm.component';
import { NgModule } from '@angular/core';



@NgModule({
  declarations: [ConfirmComponent],
  exports: [ConfirmComponent],
  entryComponents: [ConfirmComponent],
  providers: [ConfirmService],
})
export class ConfirmServiceModule {}
