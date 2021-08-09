import { BrowserModule } from '@angular/platform-browser';
import { NgModule, Injector } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { createCustomElement } from '@angular/elements';

import { AppComponent } from './app.component';
import { ExcluyenteComponent } from './components/excluyente/excluyente.component';
import { APIService } from './services/api.service';
import { AditivaComponent } from './components/aditiva/aditiva.component';
import { TextoComponent } from './components/texto/texto.component';
import { EstrellasComponent } from './components/estrellas/estrellas.component';
import { PulgaresComponent } from './components/pulgares/pulgares.component';
import { CookieService } from 'ngx-cookie-service';

@NgModule({
  declarations: [
    AppComponent,
    ExcluyenteComponent,
    AditivaComponent,
    TextoComponent,
    EstrellasComponent,
    PulgaresComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule
  ],
  providers: [
    APIService,
    CookieService
  ],
  entryComponents: [AppComponent],
  bootstrap: []
})
export class AppModule {
  constructor(private injector: Injector) {
  }
  ngDoBootstrap() { 
    const el = createCustomElement(AppComponent, { injector: this.injector });
    customElements.define('admin-encuesta', el);
  }
}

