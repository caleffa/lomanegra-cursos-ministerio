import { ConfirmServiceModule } from './services/confirm/confirm-service.module';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule, Injector } from '@angular/core';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { createCustomElement } from '@angular/elements';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { TreeModule } from 'angular-tree-component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

import { HttpErrorInterceptor } from './http-error.interceptor';
import { CoursesAPIService } from './services/api.service';
import { AppComponent } from './app.component';
import { SegmentComponent } from './components/segment/segment.component';
import { OrderModalComponent } from './components/order-modal/order-modal.component';
import { SegmentSectionComponent } from './components/segment-section/segment-section.component';
import { QuestionComponent } from './components/question/question.component';
import { OptionComponent } from './components/option/option.component';
import { SlideComponent } from './components/slide/slide.component';
import { DownloadableDocumentComponent } from './components/downloadable-document/downloadable-document.component';
import { ForumComponent } from './components/forum/forum.component';
import { CookieService } from 'ngx-cookie-service';
import { TareaComponent } from './components/tarea/tarea.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import {LiveStreamComponent} from "./components/live-stream/live-stream.component";
import {EditLiveStreamComponent} from "./components/edit-live-stream/edit-live-stream.component";

@NgModule({
  declarations: [
      AppComponent,
      OrderModalComponent,
      SegmentComponent,
      SegmentSectionComponent,
      QuestionComponent,
      OptionComponent,
      SlideComponent,
      DownloadableDocumentComponent,
      ForumComponent,
      TareaComponent,
      LiveStreamComponent,
      EditLiveStreamComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    TreeModule.forRoot(),
    NgbModule,
    ReactiveFormsModule,
    BrowserAnimationsModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    ConfirmServiceModule,
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: HttpErrorInterceptor,
      multi: true,
    },
    CoursesAPIService,
    CookieService
  ],
  entryComponents: [AppComponent, EditLiveStreamComponent],
  bootstrap: []
})
export class AppModule {
  constructor(private injector: Injector) {
  }
  ngDoBootstrap() {
    const el = createCustomElement(AppComponent, { injector: this.injector });
    customElements.define('arbol-curso', el);

    const el2 = createCustomElement(EditLiveStreamComponent, { injector: this.injector });
    customElements.define('edit-live-stream', el2);
  }
}
