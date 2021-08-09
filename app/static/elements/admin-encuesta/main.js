(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["main"],{

/***/ "./src/$$_lazy_route_resource lazy recursive":
/*!**********************************************************!*\
  !*** ./src/$$_lazy_route_resource lazy namespace object ***!
  \**********************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

function webpackEmptyAsyncContext(req) {
	// Here Promise.resolve().then() is used instead of new Promise() to prevent
	// uncaught exception popping up in devtools
	return Promise.resolve().then(function() {
		var e = new Error("Cannot find module '" + req + "'");
		e.code = 'MODULE_NOT_FOUND';
		throw e;
	});
}
webpackEmptyAsyncContext.keys = function() { return []; };
webpackEmptyAsyncContext.resolve = webpackEmptyAsyncContext;
module.exports = webpackEmptyAsyncContext;
webpackEmptyAsyncContext.id = "./src/$$_lazy_route_resource lazy recursive";

/***/ }),

/***/ "./src/app/app.component.html":
/*!************************************!*\
  !*** ./src/app/app.component.html ***!
  \************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<i class=\"fas fa-plus-circle mr-2\" (click)=\"add()\"></i>\n<select #tipoPregunta id=\"tipo-pregunta\">\n    <option value=\"EXCLUYENTE\" selected>Excluyente</option>\n    <option value=\"ADITIVA\">Aditiva</option>\n    <option value=\"TEXTO\">Texto</option>\n    <option value=\"ESTRELLAS\">Estrellas</option>\n    <option value=\"PULGARES\">Pulgares</option>\n</select>\n\n<br>\n<br>\n\n<div *ngFor=\"let cont of controllers\">\n    <div class=\"row\">\n        <div class=\"col-11\">\n\n            <div *ngIf=\"cont.getTipo() == 'EXCLUYENTE'\">\n                <app-excluyente [controller]=\"cont\" (reload)=\"reload()\"></app-excluyente>\n            </div>\n            <div *ngIf=\"cont.getTipo() == 'ADITIVA'\">\n                <app-aditiva [controller]=\"cont\" (reload)=\"reload()\"></app-aditiva>\n            </div>\n            <div *ngIf=\"cont.getTipo() == 'TEXTO'\">\n                <app-texto [controller]=\"cont\" (reload)=\"reload()\"></app-texto>\n            </div>\n            <div *ngIf=\"cont.getTipo() == 'ESTRELLAS'\">\n                <app-estrellas [controller]=\"cont\" (reload)=\"reload()\"></app-estrellas>\n            </div>\n            <div *ngIf=\"cont.getTipo() == 'PULGARES'\">\n                <app-pulgares [controller]=\"cont\" (reload)=\"reload()\"></app-pulgares>\n            </div>\n\n        </div>\n        <div class=\"col-1\">\n            <i class=\"fas fa-trash\" (click)=\"delete(cont.getId())\"></i>\n            <br>\n            <i class=\"fas fa-edit\" (click)=\"edit(cont)\"></i>\n            <br>\n            <i class=\"fas fa-long-arrow-alt-up\" (click)=\"setOrder(cont.getId(), true)\"></i>\n            <br>\n            <i class=\"fas fa-long-arrow-alt-down\" (click)=\"setOrder(cont.getId(), false)\"></i>\n        </div>\n    </div>\n    <br>\n</div>"

/***/ }),

/***/ "./src/app/app.component.scss":
/*!************************************!*\
  !*** ./src/app/app.component.scss ***!
  \************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = ".fa-plus-circle {\n  font-size: 35px; }\n\n.tipo-pregunta {\n  margin-top: -5px; }\n\n.fa-long-arrow-alt-up, .fa-long-arrow-alt-down {\n  font-size: 27px; }\n\n/*# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi9Vc2Vycy9pdmlzc2FuaS9sb21hbmVncmEtY3Vyc29zL2Zyb250ZW5kL2FkbWluLWVuY3Vlc3RhL3NyYy9hcHAvYXBwLmNvbXBvbmVudC5zY3NzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUFBO0VBQ0ksZUFBZSxFQUFBOztBQUduQjtFQUNJLGdCQUFnQixFQUFBOztBQUdwQjtFQUNJLGVBQWUsRUFBQSIsImZpbGUiOiJzcmMvYXBwL2FwcC5jb21wb25lbnQuc2NzcyIsInNvdXJjZXNDb250ZW50IjpbIi5mYS1wbHVzLWNpcmNsZSB7XG4gICAgZm9udC1zaXplOiAzNXB4O1xufVxuXG4udGlwby1wcmVndW50YSB7XG4gICAgbWFyZ2luLXRvcDogLTVweDtcbn1cblxuLmZhLWxvbmctYXJyb3ctYWx0LXVwLCAuZmEtbG9uZy1hcnJvdy1hbHQtZG93biB7XG4gICAgZm9udC1zaXplOiAyN3B4O1xufSJdfQ== */"

/***/ }),

/***/ "./src/app/app.component.ts":
/*!**********************************!*\
  !*** ./src/app/app.component.ts ***!
  \**********************************/
/*! exports provided: AppComponent, Controller */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AppComponent", function() { return AppComponent; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Controller", function() { return Controller; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm2015/core.js");
/* harmony import */ var _services_api_service__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./services/api.service */ "./src/app/services/api.service.ts");
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/forms */ "./node_modules/@angular/forms/fesm2015/forms.js");
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! rxjs */ "./node_modules/rxjs/_esm2015/index.js");





let AppComponent = class AppComponent {
    constructor(apiService, fb) {
        this.apiService = apiService;
        this.fb = fb;
    }
    ngOnInit() {
        this.reload();
    }
    reload() {
        this.apiService.get(this.encuestaId).subscribe(rta => {
            this.controllers = new Array();
            rta.forEach(preg => {
                let fg = this.getFormGroup(preg);
                this.controllers.push(new Controller(fg));
            });
        });
    }
    getFormGroup(data) {
        let fg = this.fb.group({
            id: [''],
            encuesta: ['', _angular_forms__WEBPACK_IMPORTED_MODULE_3__["Validators"].required],
            tipo: ['', _angular_forms__WEBPACK_IMPORTED_MODULE_3__["Validators"].required],
            texto: ['', _angular_forms__WEBPACK_IMPORTED_MODULE_3__["Validators"].required],
            imagen: [''],
            imagen_url: [''],
            aditiva_debe_contestar_al_menos_una: [false, _angular_forms__WEBPACK_IMPORTED_MODULE_3__["Validators"].required],
            texto_estrella_1: [''],
            texto_estrella_2: [''],
            texto_estrella_3: [''],
            texto_estrella_4: [''],
            texto_estrella_5: [''],
            texto_pulgar_arriba: [''],
            texto_pulgar_abajo: [''],
            imagen_pulgar_arriba: [''],
            imagen_pulgar_arriba_url: [''],
            imagen_pulgar_abajo: [''],
            imagen_pulgar_abajo_url: ['']
        });
        let opFormArray = this.fb.array([]);
        fg.addControl('opciones', opFormArray);
        if (data) {
            fg.patchValue(data);
            this.initOptiones(data.opciones, opFormArray);
        }
        return fg;
    }
    initOptiones(opciones, fArr) {
        opciones.forEach(o => {
            fArr.push(this.fb.group({
                id: [o.id],
                texto: [o.texto, _angular_forms__WEBPACK_IMPORTED_MODULE_3__["Validators"].required]
            }));
        });
    }
    add() {
        let fg = this.getFormGroup();
        fg.controls['tipo'].setValue(this.tipoPregunta.nativeElement.value);
        fg.controls['encuesta'].setValue(this.encuestaId);
        let newController = new Controller(fg, new rxjs__WEBPACK_IMPORTED_MODULE_4__["BehaviorSubject"](true));
        this.controllers = [newController, ...this.controllers];
    }
    delete(id) {
        this.apiService.delete(id).subscribe(_ => this.reload());
    }
    edit(controller) {
        controller.isEditing.next(true);
    }
    setOrder(id, up) {
        let currentOrder = new Array();
        this.controllers.forEach(c => {
            currentOrder.push(c.getId());
        });
        let index = currentOrder.indexOf(id);
        let newIndex;
        if (up && index != 0) {
            newIndex = index - 1;
        }
        else if (!up && index != currentOrder.length - 1) {
            newIndex = index + 1;
        }
        if (newIndex != undefined) {
            currentOrder = this.array_move(currentOrder, index, newIndex);
            this.apiService.setPreguntasOrder(this.encuestaId, currentOrder).subscribe(rta => {
                this.reload();
            });
        }
    }
    array_move(arr, old_index, new_index) {
        if (new_index >= arr.length) {
            var k = new_index - arr.length + 1;
            while (k--) {
                arr.push(undefined);
            }
        }
        arr.splice(new_index, 0, arr.splice(old_index, 1)[0]);
        return arr; // for testing
    }
};
tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Input"])('encuesta_id'),
    tslib__WEBPACK_IMPORTED_MODULE_0__["__metadata"]("design:type", Number)
], AppComponent.prototype, "encuestaId", void 0);
tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["ViewChild"])('tipoPregunta'),
    tslib__WEBPACK_IMPORTED_MODULE_0__["__metadata"]("design:type", _angular_core__WEBPACK_IMPORTED_MODULE_1__["ElementRef"])
], AppComponent.prototype, "tipoPregunta", void 0);
AppComponent = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Component"])({
        selector: 'admin-encuesta',
        template: __webpack_require__(/*! ./app.component.html */ "./src/app/app.component.html"),
        styles: [__webpack_require__(/*! ./app.component.scss */ "./src/app/app.component.scss")]
    }),
    tslib__WEBPACK_IMPORTED_MODULE_0__["__metadata"]("design:paramtypes", [_services_api_service__WEBPACK_IMPORTED_MODULE_2__["APIService"],
        _angular_forms__WEBPACK_IMPORTED_MODULE_3__["FormBuilder"]])
], AppComponent);

class Controller {
    constructor(formGroup, isEditing = new rxjs__WEBPACK_IMPORTED_MODULE_4__["BehaviorSubject"](false)) {
        this.formGroup = formGroup;
        this.isEditing = isEditing;
        this.formGroup.controls.imagen.setValue(null);
        this.formGroup.controls.imagen_pulgar_arriba.setValue(null);
        this.formGroup.controls.imagen_pulgar_abajo.setValue(null);
    }
    getTipo() {
        return this.formGroup.value.tipo;
    }
    getId() {
        return this.formGroup.value.id;
    }
}


/***/ }),

/***/ "./src/app/app.module.ts":
/*!*******************************!*\
  !*** ./src/app/app.module.ts ***!
  \*******************************/
/*! exports provided: AppModule */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AppModule", function() { return AppModule; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_platform_browser__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/platform-browser */ "./node_modules/@angular/platform-browser/fesm2015/platform-browser.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm2015/core.js");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/common/http */ "./node_modules/@angular/common/fesm2015/http.js");
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/forms */ "./node_modules/@angular/forms/fesm2015/forms.js");
/* harmony import */ var _angular_elements__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/elements */ "./node_modules/@angular/elements/fesm2015/elements.js");
/* harmony import */ var _app_component__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./app.component */ "./src/app/app.component.ts");
/* harmony import */ var _components_excluyente_excluyente_component__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./components/excluyente/excluyente.component */ "./src/app/components/excluyente/excluyente.component.ts");
/* harmony import */ var _services_api_service__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./services/api.service */ "./src/app/services/api.service.ts");
/* harmony import */ var _components_aditiva_aditiva_component__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./components/aditiva/aditiva.component */ "./src/app/components/aditiva/aditiva.component.ts");
/* harmony import */ var _components_texto_texto_component__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./components/texto/texto.component */ "./src/app/components/texto/texto.component.ts");
/* harmony import */ var _components_estrellas_estrellas_component__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./components/estrellas/estrellas.component */ "./src/app/components/estrellas/estrellas.component.ts");
/* harmony import */ var _components_pulgares_pulgares_component__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./components/pulgares/pulgares.component */ "./src/app/components/pulgares/pulgares.component.ts");
/* harmony import */ var ngx_cookie_service__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ngx-cookie-service */ "./node_modules/ngx-cookie-service/ngx-cookie-service.js");














let AppModule = class AppModule {
    constructor(injector) {
        this.injector = injector;
    }
    ngDoBootstrap() {
        const el = Object(_angular_elements__WEBPACK_IMPORTED_MODULE_5__["createCustomElement"])(_app_component__WEBPACK_IMPORTED_MODULE_6__["AppComponent"], { injector: this.injector });
        customElements.define('admin-encuesta', el);
    }
};
AppModule = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_2__["NgModule"])({
        declarations: [
            _app_component__WEBPACK_IMPORTED_MODULE_6__["AppComponent"],
            _components_excluyente_excluyente_component__WEBPACK_IMPORTED_MODULE_7__["ExcluyenteComponent"],
            _components_aditiva_aditiva_component__WEBPACK_IMPORTED_MODULE_9__["AditivaComponent"],
            _components_texto_texto_component__WEBPACK_IMPORTED_MODULE_10__["TextoComponent"],
            _components_estrellas_estrellas_component__WEBPACK_IMPORTED_MODULE_11__["EstrellasComponent"],
            _components_pulgares_pulgares_component__WEBPACK_IMPORTED_MODULE_12__["PulgaresComponent"]
        ],
        imports: [
            _angular_platform_browser__WEBPACK_IMPORTED_MODULE_1__["BrowserModule"],
            _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpClientModule"],
            _angular_forms__WEBPACK_IMPORTED_MODULE_4__["FormsModule"],
            _angular_forms__WEBPACK_IMPORTED_MODULE_4__["ReactiveFormsModule"]
        ],
        providers: [
            _services_api_service__WEBPACK_IMPORTED_MODULE_8__["APIService"],
            ngx_cookie_service__WEBPACK_IMPORTED_MODULE_13__["CookieService"]
        ],
        entryComponents: [_app_component__WEBPACK_IMPORTED_MODULE_6__["AppComponent"]],
        bootstrap: []
    }),
    tslib__WEBPACK_IMPORTED_MODULE_0__["__metadata"]("design:paramtypes", [_angular_core__WEBPACK_IMPORTED_MODULE_2__["Injector"]])
], AppModule);



/***/ }),

/***/ "./src/app/components/aditiva/aditiva.component.html":
/*!***********************************************************!*\
  !*** ./src/app/components/aditiva/aditiva.component.html ***!
  \***********************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<div class=\"card\">\n    <div class=\"card-header\">\n        Pregunta aditiva\n    </div>\n    <div class=\"card-body\">\n        <form [formGroup]=\"controller.formGroup\">\n            <div class=\"row\">\n\n                <div class=\"col-6\">\n                    Opciones:\n                    <div *ngFor=\"let opcion of getOpciones(); let i = index; trackBy: trackByFn\" formArrayName=\"opciones\">\n                        <div [formGroupName]=\"i\" class=\"row\">\n                            <div class=\"input-group mb-3\">\n                                <input type=\"text\" class=\"form-control\" placeholder=\"Respuesta {{i+1}}\" formControlName=\"texto\">\n                                <div class=\"input-group-append\">\n                                    <span (click)=\"removeOpcion(opcion, i)\" class=\"input-group-text\" id=\"basic-addon2\">\n                                        <i class=\"fas fa-trash\"></i>\n                                    </span>\n                                </div>\n                            </div>\n                        </div>\n                    </div>\n                    <div class=\"validation-errors\" >\n                        <div class=\"error-message\" *ngIf=\"noOpcion\">\n                            Debe ingresar opciones\n                        </div>\n                    </div>\n                    \n                    <div class=\"hover\" [hidden]=\"!controller.isEditing.value\" (click)=\"addOption()\">\n                        <i class=\"fas fa-plus-circle mr-2\"></i> Agregar mas opciones\n                    </div>\n                </div>\n\n                <div class=\"col-6\">\n                    <label>Texto pregunta</label>\n                    <textarea formControlName=\"texto\" class=\"form-control\"></textarea>\n                    <div class=\"validation-errors\" *ngFor=\"let validation of validationMessages.texto\">\n                        <div class=\"error-message\" *ngIf=\"showErrors('texto', validation)\">\n                            {{ validation.message }}\n                        </div>\n                    </div>\n\n                    <label>Imagen</label>\n                    <div [hidden]=\"!getImageUrl('imagen_url')\" class=\"card\">\n                        <div class=\"card-body\">\n                            <img src=\"{{ getImageUrl('imagen_url') }}\" class=\"imagen-preview\"/>\n                        </div>\n                    </div>\n                    <input type=\"file\" (change)=\"uploadImage($event, 'imagen')\"  accept=\".png, .jpg, .jpeg, .gif\" [hidden]=\"!controller.isEditing.value\"/>\n\n                </div>\n            </div>\n        </form>\n    </div>\n    <div class=\"card-footer\" [hidden]=\"!controller.isEditing.value\">\n        <button class=\"btn btn-success float-right ml-2\" (click)=\"save()\" [disabled]=\"!controller.formGroup.valid || noOpcion\">Aceptar</button>\n        <button class=\"btn btn-danger float-right\" (click)=\"reset()\" >Cancelar</button>\n    </div>\n</div>\n\n"

/***/ }),

/***/ "./src/app/components/aditiva/aditiva.component.scss":
/*!***********************************************************!*\
  !*** ./src/app/components/aditiva/aditiva.component.scss ***!
  \***********************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "\n/*# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsImZpbGUiOiJzcmMvYXBwL2NvbXBvbmVudHMvYWRpdGl2YS9hZGl0aXZhLmNvbXBvbmVudC5zY3NzIn0= */"

/***/ }),

/***/ "./src/app/components/aditiva/aditiva.component.ts":
/*!*********************************************************!*\
  !*** ./src/app/components/aditiva/aditiva.component.ts ***!
  \*********************************************************/
/*! exports provided: AditivaComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AditivaComponent", function() { return AditivaComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm2015/core.js");
/* harmony import */ var _base_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../base.component */ "./src/app/components/base.component.ts");



let AditivaComponent = class AditivaComponent extends _base_component__WEBPACK_IMPORTED_MODULE_2__["BaseComponent"] {
    ngOnInit() {
        super.ngOnInit();
        if (!this.controller.formGroup.value.id) {
            this.addOption();
        }
        this.controller.formGroup.controls['aditiva_debe_contestar_al_menos_una'].setValue(true);
    }
};
AditivaComponent = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Component"])({
        selector: 'app-aditiva',
        template: __webpack_require__(/*! ./aditiva.component.html */ "./src/app/components/aditiva/aditiva.component.html"),
        styles: [__webpack_require__(/*! ./aditiva.component.scss */ "./src/app/components/aditiva/aditiva.component.scss")]
    })
], AditivaComponent);



/***/ }),

/***/ "./src/app/components/base.component.ts":
/*!**********************************************!*\
  !*** ./src/app/components/base.component.ts ***!
  \**********************************************/
/*! exports provided: BaseComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "BaseComponent", function() { return BaseComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm2015/core.js");
/* harmony import */ var _app_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../app.component */ "./src/app/app.component.ts");
/* harmony import */ var _services_api_service__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../services/api.service */ "./src/app/services/api.service.ts");
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/forms */ "./node_modules/@angular/forms/fesm2015/forms.js");





let BaseComponent = class BaseComponent {
    constructor(apiService, fb) {
        this.apiService = apiService;
        this.fb = fb;
        this.reload = new _angular_core__WEBPACK_IMPORTED_MODULE_1__["EventEmitter"]();
        this.optionsToDelete = new Array();
    }
    ngOnInit() {
        this.controller.isEditing.subscribe(val => {
            if (val) {
                this.controller.formGroup.enable();
            }
            else {
                this.controller.formGroup.disable();
            }
        });
        this.initValidationMessages();
        this.noOpcion = this.getOpciones().length == 0;
    }
    trackByFn(index, item) {
        return index;
    }
    initValidationMessages() {
        this.validationMessages = {
            'texto': [{ type: 'required', message: 'Ingrese un texto' }]
        };
    }
    showErrors(controlName, validation) {
        const control = this.controller.formGroup.get(controlName);
        return control.hasError(validation.type);
    }
    getImageUrl(imagen) {
        return this.controller.formGroup.value[imagen];
    }
    getOpciones() {
        return this.controller.formGroup['controls'].opciones.value;
    }
    addOption() {
        this.controller.formGroup['controls'].opciones['push'](this.fb.group({
            texto: ['', _angular_forms__WEBPACK_IMPORTED_MODULE_4__["Validators"].required]
        }));
        this.noOpcion = false;
    }
    removeOpcion(opcion, index) {
        if (this.controller.isEditing.value) {
            let formAr = this.controller.formGroup['controls'].opciones;
            formAr.removeAt(index);
            this.optionsToDelete.push(opcion);
        }
        this.noOpcion = this.getOpciones().length == 0;
    }
    uploadImage(event, imgFieldName) {
        if (event.target.files && event.target.files[0]) {
            let reader = new FileReader();
            reader.onload = () => {
                this.controller.formGroup.get(imgFieldName).setValue(event.target.files[0]);
            };
            reader.readAsDataURL(event.target.files[0]);
        }
    }
    save() {
        if (this.controller.formGroup.valid) {
            let observable;
            let controls = this.controller.formGroup.controls;
            let data = new FormData();
            Object.keys(controls).forEach(key => {
                if (controls[key].value && key != 'opciones') {
                    data.append(key, controls[key].value);
                }
                else if (key == 'opciones') {
                    let json = JSON.stringify(controls[key].value);
                    data.append('opciones_json', json);
                }
            });
            if (controls['id'].value) {
                observable = this.apiService.update(controls['id'].value.toString(), data);
                this.deleteOpciones();
            }
            else {
                observable = this.apiService.create(data);
            }
            observable.subscribe(rta => {
                this.reset();
            });
        }
    }
    deleteOpciones() {
        let opciones = this.optionsToDelete.filter(o => o == o);
        opciones.forEach(op => {
            this.apiService.deleteOpcion(op.id).subscribe(_ => { });
            this.optionsToDelete = this.optionsToDelete.fill(o => o != op);
        });
    }
    reset() {
        this.reload.emit();
        this.optionsToDelete = new Array();
    }
};
tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Input"])(),
    tslib__WEBPACK_IMPORTED_MODULE_0__["__metadata"]("design:type", _app_component__WEBPACK_IMPORTED_MODULE_2__["Controller"])
], BaseComponent.prototype, "controller", void 0);
tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Output"])('reload'),
    tslib__WEBPACK_IMPORTED_MODULE_0__["__metadata"]("design:type", _angular_core__WEBPACK_IMPORTED_MODULE_1__["EventEmitter"])
], BaseComponent.prototype, "reload", void 0);
BaseComponent = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Injectable"])(),
    tslib__WEBPACK_IMPORTED_MODULE_0__["__metadata"]("design:paramtypes", [_services_api_service__WEBPACK_IMPORTED_MODULE_3__["APIService"],
        _angular_forms__WEBPACK_IMPORTED_MODULE_4__["FormBuilder"]])
], BaseComponent);



/***/ }),

/***/ "./src/app/components/estrellas/estrellas.component.html":
/*!***************************************************************!*\
  !*** ./src/app/components/estrellas/estrellas.component.html ***!
  \***************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<div class=\"card\">\n    <div class=\"card-header\">\n        Pregunta de estrellas\n    </div>\n    <div class=\"card-body\">\n        <form [formGroup]=\"controller.formGroup\">\n            <div class=\"row\">\n                <div class=\"col-6\">\n                    <label>Texto pregunta</label>\n                    <textarea formControlName=\"texto\" class=\"form-control\"></textarea>\n                    <div class=\"validation-errors\" *ngFor=\"let validation of validationMessages.texto\">\n                        <div class=\"error-message\" *ngIf=\"showErrors('texto', validation)\">\n                            {{ validation.message }}\n                        </div>\n                    </div>\n                </div>\n\n                <div class=\"col-6\">\n                    <label>Imagen</label>\n                    <div [hidden]=\"!getImageUrl('imagen_url')\" class=\"card\">\n                        <div class=\"card-body\">\n                            <img src=\"{{ getImageUrl('imagen_url') }}\" class=\"imagen-preview\"/>\n                        </div>\n                    </div>\n                    <input type=\"file\" (change)=\"uploadImage($event, 'imagen')\"  accept=\".png, .jpg, .jpeg, .gif\" [hidden]=\"!controller.isEditing.value\"/>\n                </div>\n            </div>\n\n            <br>\n\n            <div class=\"row\">\n\n                <div class=\"col-2 star-col\">\n                    <i class=\"fas fa-star mb-2\"></i>\n                    <input type=\"text\" class=\"form-control\" formControlName=\"texto_estrella_1\">\n                </div>\n\n                <div class=\"col-2 star-col\">\n                    <i class=\"fas fa-star mb-2\"></i>\n                    <input type=\"text\" class=\"form-control\" formControlName=\"texto_estrella_2\">\n                </div>\n\n                <div class=\"col-2 star-col\">\n                    <i class=\"fas fa-star mb-2\"></i>\n                    <input type=\"text\" class=\"form-control\" formControlName=\"texto_estrella_3\">\n                </div>\n\n                <div class=\"col-2 star-col\">\n                    <i class=\"fas fa-star mb-2\"></i>\n                    <input type=\"text\" class=\"form-control\" formControlName=\"texto_estrella_4\">\n                </div>\n\n                <div class=\"col-2 star-col\">\n                    <i class=\"fas fa-star mb-2\"></i>\n                    <input type=\"text\" class=\"form-control\" formControlName=\"texto_estrella_5\">\n                </div>\n\n            </div>\n        </form>\n    </div>\n    <div class=\"card-footer\" [hidden]=\"!controller.isEditing.value\">\n        <button class=\"btn btn-success float-right ml-2\" (click)=\"save()\" [disabled]=\"!controller.formGroup.valid\">Aceptar</button>\n        <button class=\"btn btn-danger float-right\" (click)=\"reset()\" >Cancelar</button>\n    </div>\n</div>\n\n"

/***/ }),

/***/ "./src/app/components/estrellas/estrellas.component.scss":
/*!***************************************************************!*\
  !*** ./src/app/components/estrellas/estrellas.component.scss ***!
  \***************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = ".star-col {\n  text-align: center; }\n\n.fa-star {\n  font-size: 35px; }\n\n/*# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi9Vc2Vycy9pdmlzc2FuaS9sb21hbmVncmEtY3Vyc29zL2Zyb250ZW5kL2FkbWluLWVuY3Vlc3RhL3NyYy9hcHAvY29tcG9uZW50cy9lc3RyZWxsYXMvZXN0cmVsbGFzLmNvbXBvbmVudC5zY3NzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUFBO0VBQ0ksa0JBQWtCLEVBQUE7O0FBR3RCO0VBQ0ksZUFBZSxFQUFBIiwiZmlsZSI6InNyYy9hcHAvY29tcG9uZW50cy9lc3RyZWxsYXMvZXN0cmVsbGFzLmNvbXBvbmVudC5zY3NzIiwic291cmNlc0NvbnRlbnQiOlsiLnN0YXItY29sIHtcbiAgICB0ZXh0LWFsaWduOiBjZW50ZXI7XG59XG5cbi5mYS1zdGFyIHtcbiAgICBmb250LXNpemU6IDM1cHg7XG59XG4iXX0= */"

/***/ }),

/***/ "./src/app/components/estrellas/estrellas.component.ts":
/*!*************************************************************!*\
  !*** ./src/app/components/estrellas/estrellas.component.ts ***!
  \*************************************************************/
/*! exports provided: EstrellasComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "EstrellasComponent", function() { return EstrellasComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm2015/core.js");
/* harmony import */ var _base_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../base.component */ "./src/app/components/base.component.ts");



let EstrellasComponent = class EstrellasComponent extends _base_component__WEBPACK_IMPORTED_MODULE_2__["BaseComponent"] {
};
EstrellasComponent = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Component"])({
        selector: 'app-estrellas',
        template: __webpack_require__(/*! ./estrellas.component.html */ "./src/app/components/estrellas/estrellas.component.html"),
        styles: [__webpack_require__(/*! ./estrellas.component.scss */ "./src/app/components/estrellas/estrellas.component.scss")]
    })
], EstrellasComponent);



/***/ }),

/***/ "./src/app/components/excluyente/excluyente.component.html":
/*!*****************************************************************!*\
  !*** ./src/app/components/excluyente/excluyente.component.html ***!
  \*****************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<div class=\"card\">\n    <div class=\"card-header\">\n        Pregunta excluyente\n    </div>\n    <div class=\"card-body\">\n        <form [formGroup]=\"controller.formGroup\">\n            <div class=\"row\">\n\n                <div class=\"col-6\">\n                    Opciones:\n                    <div *ngFor=\"let opcion of getOpciones(); index as i; trackBy: trackByFn\" formArrayName=\"opciones\">\n                        <div [formGroupName]=\"i\" class=\"row\">\n                            <div class=\"input-group mb-3\">\n                                <input type=\"text\" class=\"form-control\" placeholder=\"Respuesta {{i+1}}\" formControlName=\"texto\">\n                                <div class=\"input-group-append\">\n                                    <span (click)=\"removeOpcion(opcion, i)\" class=\"input-group-text\" id=\"basic-addon2\">\n                                        <i class=\"fas fa-trash\"></i>\n                                    </span>\n                                </div>\n                            </div>\n                        </div>\n                    </div>\n                    <div class=\"validation-errors\" >\n                        <div class=\"error-message\" *ngIf=\"noOpcion\">\n                            Debe ingresar opciones\n                        </div>\n                    </div>\n                    \n                    <div class=\"hover\" [hidden]=\"!controller.isEditing.value\" (click)=\"addOption()\">\n                        <i class=\"fas fa-plus-circle mr-2\"></i> Agregar mas opciones\n                    </div>\n                </div>\n\n                <div class=\"col-6\">\n                    <label>Texto pregunta</label>\n                    <textarea formControlName=\"texto\" class=\"form-control\"></textarea>\n                    <div class=\"validation-errors\" *ngFor=\"let validation of validationMessages.texto\">\n                        <div class=\"error-message\" *ngIf=\"showErrors('texto', validation)\">\n                            {{ validation.message }}\n                        </div>\n                    </div>\n\n                    <label>Imagen</label>\n                    <div [hidden]=\"!getImageUrl('imagen_url')\" class=\"card\">\n                        <div class=\"card-body\">\n                            <img src=\"{{ getImageUrl('imagen_url') }}\" class=\"imagen-preview\"/>\n                        </div>\n                    </div>\n                    <input type=\"file\" (change)=\"uploadImage($event, 'imagen')\"  accept=\".png, .jpg, .jpeg, .gif\" [hidden]=\"!controller.isEditing.value\"/>\n\n                </div>\n            </div>\n        </form>\n    </div>\n    <div class=\"card-footer\" [hidden]=\"!controller.isEditing.value\">\n        <button class=\"btn btn-success float-right ml-2\" (click)=\"save()\" [disabled]=\"!controller.formGroup.valid || noOpcion\">Aceptar</button>\n        <button class=\"btn btn-danger float-right\" (click)=\"reset()\" >Cancelar</button>\n    </div>\n</div>\n\n"

/***/ }),

/***/ "./src/app/components/excluyente/excluyente.component.scss":
/*!*****************************************************************!*\
  !*** ./src/app/components/excluyente/excluyente.component.scss ***!
  \*****************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "\n/*# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsImZpbGUiOiJzcmMvYXBwL2NvbXBvbmVudHMvZXhjbHV5ZW50ZS9leGNsdXllbnRlLmNvbXBvbmVudC5zY3NzIn0= */"

/***/ }),

/***/ "./src/app/components/excluyente/excluyente.component.ts":
/*!***************************************************************!*\
  !*** ./src/app/components/excluyente/excluyente.component.ts ***!
  \***************************************************************/
/*! exports provided: ExcluyenteComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ExcluyenteComponent", function() { return ExcluyenteComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm2015/core.js");
/* harmony import */ var _base_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../base.component */ "./src/app/components/base.component.ts");



let ExcluyenteComponent = class ExcluyenteComponent extends _base_component__WEBPACK_IMPORTED_MODULE_2__["BaseComponent"] {
    ngOnInit() {
        super.ngOnInit();
        if (!this.controller.formGroup.value.id) {
            this.addOption();
        }
    }
};
ExcluyenteComponent = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Component"])({
        selector: 'app-excluyente',
        template: __webpack_require__(/*! ./excluyente.component.html */ "./src/app/components/excluyente/excluyente.component.html"),
        styles: [__webpack_require__(/*! ./excluyente.component.scss */ "./src/app/components/excluyente/excluyente.component.scss")]
    })
], ExcluyenteComponent);



/***/ }),

/***/ "./src/app/components/pulgares/pulgares.component.html":
/*!*************************************************************!*\
  !*** ./src/app/components/pulgares/pulgares.component.html ***!
  \*************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<div class=\"card\">\n    <div class=\"card-header\">\n        Pregunta de pulgares\n    </div>\n    <div class=\"card-body\">\n        <form [formGroup]=\"controller.formGroup\">\n            <div class=\"row\">\n                <div class=\"col-6\">\n                    <label>Texto pregunta</label>\n                    <textarea formControlName=\"texto\" class=\"form-control\"></textarea>\n                    <div class=\"validation-errors\" *ngFor=\"let validation of validationMessages.texto\">\n                        <div class=\"error-message\" *ngIf=\"showErrors('texto', validation)\">\n                            {{ validation.message }}\n                        </div>\n                    </div>\n                </div>\n\n                <div class=\"col-6\">\n                    <label>Imagen</label>\n                    <div [hidden]=\"!getImageUrl('imagen_url')\" class=\"card\">\n                        <div class=\"card-body\">\n                            <img src=\"{{ getImageUrl('imagen_url') }}\" class=\"imagen-preview\"/>\n                        </div>\n                    </div>\n                    <input type=\"file\" (change)=\"uploadImage($event, 'imagen')\"  accept=\".png, .jpg, .jpeg, .gif\" [hidden]=\"!controller.isEditing.value\"/>\n                </div>\n            </div>\n\n            <br>\n\n            <div class=\"row\">\n\n                <div class=\"col-6\">\n                    <label>Opcion 1</label>\n                    <div class=\"card\">\n                        <div class=\"card-body pulgar-card\">\n                            <label>Imagen</label>\n                            <img [hidden]=\"!getImageUrl('imagen_pulgar_arriba_url')\" \n                                src=\"{{ getImageUrl('imagen_pulgar_arriba_url') }}\" class=\"imagen-preview\"/>\n                            <i class=\"fas fa-thumbs-up\" [hidden]=\"getImageUrl('imagen_pulgar_arriba_url')\" ></i>\n                            <input type=\"file\" (change)=\"uploadImage($event, 'imagen_pulgar_arriba')\"  accept=\".png, .jpg, .jpeg, .gif\" [hidden]=\"!controller.isEditing.value\"/>\n                            <br>\n                            <label>Texto</label>\n                            <input type=\"text\" class=\"form-control\" formControlName=\"texto_pulgar_arriba\"/>\n                        </div>\n                    </div>\n                </div>\n\n                <div class=\"col-6\">\n                    <label>Opcion 2</label>\n                    <div class=\"card\">\n                        <div class=\"card-body pulgar-card\">\n                            <label>Imagen</label>\n                            <img [hidden]=\"!getImageUrl('imagen_pulgar_abajo_url')\" \n                                src=\"{{ getImageUrl('imagen_pulgar_abajo_url') }}\" class=\"imagen-preview\"/>\n                            <i class=\"fas fa-thumbs-down\" [hidden]=\"getImageUrl('imagen_pulgar_abajo_url')\" ></i>\n                            <input type=\"file\" (change)=\"uploadImage($event, 'imagen_pulgar_abajo')\"  accept=\".png, .jpg, .jpeg, .gif\" [hidden]=\"!controller.isEditing.value\"/>\n                            <br>\n                            <label>Texto</label>\n                            <input type=\"text\" class=\"form-control\" formControlName=\"texto_pulgar_abajo\"/>\n                        </div>\n                    </div>\n                </div>\n\n            </div>\n        </form>\n    </div>\n    <div class=\"card-footer\" [hidden]=\"!controller.isEditing.value\">\n        <button class=\"btn btn-success float-right ml-2\" (click)=\"save()\" [disabled]=\"!controller.formGroup.valid\">Aceptar</button>\n        <button class=\"btn btn-danger float-right\" (click)=\"reset()\" >Cancelar</button>\n    </div>\n</div>\n\n"

/***/ }),

/***/ "./src/app/components/pulgares/pulgares.component.scss":
/*!*************************************************************!*\
  !*** ./src/app/components/pulgares/pulgares.component.scss ***!
  \*************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = ".pulgar-card {\n  text-align: center; }\n\n.fa-thumbs-up, .fa-down-up {\n  font-size: 35px; }\n\n/*# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi9Vc2Vycy9pdmlzc2FuaS9sb21hbmVncmEtY3Vyc29zL2Zyb250ZW5kL2FkbWluLWVuY3Vlc3RhL3NyYy9hcHAvY29tcG9uZW50cy9wdWxnYXJlcy9wdWxnYXJlcy5jb21wb25lbnQuc2NzcyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFBQTtFQUNJLGtCQUFrQixFQUFBOztBQUd0QjtFQUNJLGVBQWUsRUFBQSIsImZpbGUiOiJzcmMvYXBwL2NvbXBvbmVudHMvcHVsZ2FyZXMvcHVsZ2FyZXMuY29tcG9uZW50LnNjc3MiLCJzb3VyY2VzQ29udGVudCI6WyIucHVsZ2FyLWNhcmQge1xuICAgIHRleHQtYWxpZ246IGNlbnRlcjtcbn1cblxuLmZhLXRodW1icy11cCwgLmZhLWRvd24tdXAge1xuICAgIGZvbnQtc2l6ZTogMzVweDtcbn0iXX0= */"

/***/ }),

/***/ "./src/app/components/pulgares/pulgares.component.ts":
/*!***********************************************************!*\
  !*** ./src/app/components/pulgares/pulgares.component.ts ***!
  \***********************************************************/
/*! exports provided: PulgaresComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "PulgaresComponent", function() { return PulgaresComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm2015/core.js");
/* harmony import */ var _base_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../base.component */ "./src/app/components/base.component.ts");



let PulgaresComponent = class PulgaresComponent extends _base_component__WEBPACK_IMPORTED_MODULE_2__["BaseComponent"] {
};
PulgaresComponent = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Component"])({
        selector: 'app-pulgares',
        template: __webpack_require__(/*! ./pulgares.component.html */ "./src/app/components/pulgares/pulgares.component.html"),
        styles: [__webpack_require__(/*! ./pulgares.component.scss */ "./src/app/components/pulgares/pulgares.component.scss")]
    })
], PulgaresComponent);



/***/ }),

/***/ "./src/app/components/texto/texto.component.html":
/*!*******************************************************!*\
  !*** ./src/app/components/texto/texto.component.html ***!
  \*******************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<div class=\"card\">\n    <div class=\"card-header\">\n        Pregunta de texto\n    </div>\n    <div class=\"card-body\">\n        <form [formGroup]=\"controller.formGroup\">\n            <div class=\"row\">\n\n                <div class=\"col-6\">\n                    <label>Texto pregunta</label>\n                    <textarea formControlName=\"texto\" class=\"form-control\"></textarea>\n                    <div class=\"validation-errors\" *ngFor=\"let validation of validationMessages.texto\">\n                        <div class=\"error-message\" *ngIf=\"showErrors('texto', validation)\">\n                            {{ validation.message }}\n                        </div>\n                    </div>\n                </div>\n\n                <div class=\"col-6\">\n                    <label>Imagen</label>\n                    <div [hidden]=\"!getImageUrl('imagen_url')\" class=\"card\">\n                        <div class=\"card-body\">\n                            <img src=\"{{ getImageUrl('imagen_url') }}\" class=\"imagen-preview\"/>\n                        </div>\n                    </div>\n                    <input type=\"file\" (change)=\"uploadImage($event, 'imagen')\"  accept=\".png, .jpg, .jpeg, .gif\" [hidden]=\"!controller.isEditing.value\"/>\n\n                </div>\n            </div>\n        </form>\n    </div>\n    <div class=\"card-footer\" [hidden]=\"!controller.isEditing.value\">\n        <button class=\"btn btn-success float-right ml-2\" (click)=\"save()\" [disabled]=\"!controller.formGroup.valid\">Aceptar</button>\n        <button class=\"btn btn-danger float-right\" (click)=\"reset()\" >Cancelar</button>\n    </div>\n</div>\n\n"

/***/ }),

/***/ "./src/app/components/texto/texto.component.scss":
/*!*******************************************************!*\
  !*** ./src/app/components/texto/texto.component.scss ***!
  \*******************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "\n/*# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsImZpbGUiOiJzcmMvYXBwL2NvbXBvbmVudHMvdGV4dG8vdGV4dG8uY29tcG9uZW50LnNjc3MifQ== */"

/***/ }),

/***/ "./src/app/components/texto/texto.component.ts":
/*!*****************************************************!*\
  !*** ./src/app/components/texto/texto.component.ts ***!
  \*****************************************************/
/*! exports provided: TextoComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "TextoComponent", function() { return TextoComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm2015/core.js");
/* harmony import */ var _base_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../base.component */ "./src/app/components/base.component.ts");



let TextoComponent = class TextoComponent extends _base_component__WEBPACK_IMPORTED_MODULE_2__["BaseComponent"] {
};
TextoComponent = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Component"])({
        selector: 'app-texto',
        template: __webpack_require__(/*! ./texto.component.html */ "./src/app/components/texto/texto.component.html"),
        styles: [__webpack_require__(/*! ./texto.component.scss */ "./src/app/components/texto/texto.component.scss")]
    })
], TextoComponent);



/***/ }),

/***/ "./src/app/services/api.service.ts":
/*!*****************************************!*\
  !*** ./src/app/services/api.service.ts ***!
  \*****************************************/
/*! exports provided: APIService */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "APIService", function() { return APIService; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm2015/core.js");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/common/http */ "./node_modules/@angular/common/fesm2015/http.js");
/* harmony import */ var url_join__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! url-join */ "./node_modules/url-join/lib/url-join.js");
/* harmony import */ var url_join__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(url_join__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var ngx_cookie_service__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ngx-cookie-service */ "./node_modules/ngx-cookie-service/ngx-cookie-service.js");
/* harmony import */ var _environments_environment__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../../environments/environment */ "./src/environments/environment.ts");






let APIService = class APIService {
    constructor(http, cookieService) {
        this.http = http;
        this.cookieService = cookieService;
        this.apiUrl = _environments_environment__WEBPACK_IMPORTED_MODULE_5__["environment"].apiUrl;
        let csrftoken = this.cookieService.get('csrftoken');
        if (csrftoken) {
            this.headers = { headers: { "X-CSRFToken": csrftoken } };
        }
    }
    get(id) {
        return this.http.get(url_join__WEBPACK_IMPORTED_MODULE_3___default()(this.apiUrl, 'encuesta/', id.toString(), '/preguntas'));
    }
    create(data) {
        return this.http.post(url_join__WEBPACK_IMPORTED_MODULE_3___default()(this.apiUrl, 'pregunta/'), data, this.headers);
    }
    update(id, data) {
        return this.http.patch(url_join__WEBPACK_IMPORTED_MODULE_3___default()(this.apiUrl, 'pregunta/', id, '/'), data, this.headers);
    }
    delete(id) {
        return this.http.delete(url_join__WEBPACK_IMPORTED_MODULE_3___default()(this.apiUrl, 'pregunta', id.toString()), this.headers);
    }
    deleteOpcion(id) {
        return this.http.delete(url_join__WEBPACK_IMPORTED_MODULE_3___default()(this.apiUrl, 'opcion_pregunta', id.toString()), this.headers);
    }
    setPreguntasOrder(encuesta, order) {
        let data = {
            encuesta: encuesta,
            order: order
        };
        return this.http.post(url_join__WEBPACK_IMPORTED_MODULE_3___default()(this.apiUrl, 'set_preguntas_order'), data, this.headers);
    }
};
APIService = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Injectable"])(),
    tslib__WEBPACK_IMPORTED_MODULE_0__["__metadata"]("design:paramtypes", [_angular_common_http__WEBPACK_IMPORTED_MODULE_2__["HttpClient"],
        ngx_cookie_service__WEBPACK_IMPORTED_MODULE_4__["CookieService"]])
], APIService);



/***/ }),

/***/ "./src/environments/environment.ts":
/*!*****************************************!*\
  !*** ./src/environments/environment.ts ***!
  \*****************************************/
/*! exports provided: environment */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "environment", function() { return environment; });
// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.
const environment = {
    production: false,
    apiUrl: ''
};
/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/dist/zone-error';  // Included with Angular CLI.


/***/ }),

/***/ "./src/main.ts":
/*!*********************!*\
  !*** ./src/main.ts ***!
  \*********************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm2015/core.js");
/* harmony import */ var _angular_platform_browser_dynamic__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/platform-browser-dynamic */ "./node_modules/@angular/platform-browser-dynamic/fesm2015/platform-browser-dynamic.js");
/* harmony import */ var _app_app_module__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./app/app.module */ "./src/app/app.module.ts");
/* harmony import */ var _environments_environment__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./environments/environment */ "./src/environments/environment.ts");




if (_environments_environment__WEBPACK_IMPORTED_MODULE_3__["environment"].production) {
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["enableProdMode"])();
}
Object(_angular_platform_browser_dynamic__WEBPACK_IMPORTED_MODULE_1__["platformBrowserDynamic"])().bootstrapModule(_app_app_module__WEBPACK_IMPORTED_MODULE_2__["AppModule"])
    .catch(err => console.error(err));


/***/ }),

/***/ 0:
/*!***************************!*\
  !*** multi ./src/main.ts ***!
  \***************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__(/*! /Users/ivissani/lomanegra-cursos/frontend/admin-encuesta/src/main.ts */"./src/main.ts");


/***/ })

},[[0,"runtime","vendor"]]]);
//# sourceMappingURL=main.js.map