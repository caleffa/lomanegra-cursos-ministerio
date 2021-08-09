import { Component, Input, ElementRef, ViewChild, OnInit } from '@angular/core';
import { APIService } from './services/api.service';
import { FormBuilder, Validators, FormGroup, FormArray } from '@angular/forms';
import { BehaviorSubject } from 'rxjs';

@Component({
  selector: 'admin-encuesta',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  @Input('encuesta_id') public encuestaId: number;
  @ViewChild('tipoPregunta') public tipoPregunta: ElementRef;

  public controllers: Controller[];

  constructor(private apiService: APIService,
    private fb: FormBuilder) {
  }

  public ngOnInit(): void {
    this.reload();
  }

  public reload(): void {
    this.apiService.get(this.encuestaId).subscribe(rta => {
      this.controllers = new Array<Controller>();
      rta.forEach(preg => {
        let fg = this.getFormGroup(preg);
        this.controllers.push(new Controller(fg));
      });
    });
  }

  private getFormGroup(data?: any): FormGroup {
    let fg = this.fb.group({
      id: [''],
      encuesta: ['', Validators.required],
      tipo: ['', Validators.required],
      texto: ['', Validators.required],
      imagen: [''],
      imagen_url: [''],
      aditiva_debe_contestar_al_menos_una: [false, Validators.required],
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
    if(data) {
      fg.patchValue(data);
      this.initOptiones(data.opciones, opFormArray);
    }
    return fg;
  }

  private initOptiones(opciones: any[], fArr: FormArray) {
    opciones.forEach(o => {
      fArr.push(this.fb.group({
        id: [o.id],
        texto: [o.texto, Validators.required]
      }))
    })
  }

  public add(): void {
    let fg = this.getFormGroup();
    fg.controls['tipo'].setValue(this.tipoPregunta.nativeElement.value);
    fg.controls['encuesta'].setValue(this.encuestaId);
    let newController = new Controller(fg, new BehaviorSubject<boolean>(true));
    this.controllers = [newController, ...this.controllers];
  }

  public delete(id: number): void {
    this.apiService.delete(id).subscribe(_=>this.reload());
  }

  public edit(controller: Controller): void {
    controller.isEditing.next(true);
  }

  public setOrder(id: number, up: boolean): void {
    let currentOrder = new Array<number>();
    this.controllers.forEach(c => {
      currentOrder.push(c.getId());
    });
    let index = currentOrder.indexOf(id);
    let newIndex;
    if(up && index != 0) {
      newIndex = index-1;
    } else if(!up && index != currentOrder.length-1) {
      newIndex = index+1;
    }
    if(newIndex != undefined) {
      currentOrder = this.array_move(currentOrder, index, newIndex);
      this.apiService.setPreguntasOrder(this.encuestaId, currentOrder).subscribe(rta => {
        this.reload();
      });
    }
  }

  public array_move(arr, old_index, new_index) {
    if (new_index >= arr.length) {
        var k = new_index - arr.length + 1;
        while (k--) {
            arr.push(undefined);
        }
    }
    arr.splice(new_index, 0, arr.splice(old_index, 1)[0]);
    return arr; // for testing
  }

  
}

export class Controller {
  constructor(public formGroup: FormGroup,
    public isEditing = new BehaviorSubject<boolean>(false)) {
    this.formGroup.controls.imagen.setValue(null);
    this.formGroup.controls.imagen_pulgar_arriba.setValue(null);
    this.formGroup.controls.imagen_pulgar_abajo.setValue(null);
  }

  public getTipo(): string {
    return this.formGroup.value.tipo; 
  }

  public getId(): number {
    return this.formGroup.value.id;
  }

}
